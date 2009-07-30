# -*- coding: utf-8 -*-

# Author: Santiago Bruno
# License: GPL v3
# Web pages: http://www.santiagobruno.com.ar/programas.html
#            http://code.google.com/p/mtvcgui/

import locale
import os
import commands
import re
import time
import ConfigParser

NORMS_DICT = {0 : 'NTSC',
              1 : 'NTSC-M',
              2 : 'NTSC-M-JP',
              3 : 'NTSC-M-KR',
              4 : 'PAL',
              5 : 'PAL-BG',
              6 : 'PAL-H',
              7 : 'PAL-I',
              8 : 'PAL-DK',
              9 : 'PAL-M',
              10 : 'PAL-N',
              11 : 'PAL-Nc',
              12 : 'PAL-60',
              13 : 'SECAM',
              14 : 'SECAM-B',
              15 : 'SECAM-G',
              16 : 'SECAM-H',
              17 : 'SECAM-DK',
              18 : 'SECAM-L',
              19 : 'SECAM-Lc'
              }

def find_translation(prefix='', tr_dir='i18n'):
    """Function to find a translation file in a directory
       and install it to an app
    """
    #try with country specific locale (e.g.: es_AR)
    lang = locale.getdefaultlocale()[0]
    if lang:
        tr_path = os.path.join(tr_dir, prefix + lang + '.qm')

        if not os.path.exists(tr_path):
            #try with generic locale (e.g.: es)
            lang = lang.split('_')[0]
            tr_path = os.path.join(tr_dir, prefix + lang + '.qm')
            if not os.path.exists(tr_path):
                #don't translate
                tr_path = ''
    else:
        tr_path = ''

    return tr_path


def get_codecs(cmd):
    """Returns available codecs from mplayer using the given command
    e.g. mencoder -ovc help
    """
    output = commands.getoutput(cmd)
    lines = output.split('\n')
    text = ''
    skip = True
    for line in lines:
        if not skip:
            text += '\n' + line
        if 'Available codecs:' in line:
            text += line
            skip = False
    if not text:
        text = output
    return text


def make_filename(filename, channel_text, append_suffix=True):
    """Generates the filename given the filename template and filling the
    variables with the date (channel or date)
    """
    def repl_func(match, now):
        year   = now[0]
        month  = now[1]
        day    = now[2]
        hour   = now[3]
        minute = now[4]
        second = now[5]

        text = match.group()

        text = text.replace('%Y', str(year))
        text = text.replace('%y', str(year)[2:])
        text = text.replace('%m', "%.2d" % month)
        text = text.replace('%d', "%.2d" % day)
        text = text.replace('%H', "%.2d" % hour)
        text = text.replace('%M', "%.2d" % minute)
        text = text.replace('%S', "%.2d" % second)
        text = text.replace('%channel', channel_text)

        return text[1:-1]

    new_filename = filename.replace('{channel}', channel_text)
    now    = time.localtime()
    new_filename = re.sub('{[^}]*?}', lambda x: repl_func(x, now), new_filename)

    if append_suffix:
        suffix = 1
        appended_filename = new_filename
        while os.path.exists(appended_filename):
            dot_splitted = new_filename.split('.')

            if len(dot_splitted) > 1:
                name = dot_splitted[:-1]
                extension = [dot_splitted[-1]]
            else:
                name = dot_splitted
                extension = []

            name[-1] = name[-1] + '_' + str(suffix)

            appended_filename = '.'.join(name + extension)
            suffix += 1
        new_filename = appended_filename

    return new_filename

def secs_to_str(seconds):
    """Convert a number of seconds to its string representation in hh:mm:ss
    """
    secs = seconds % 60
    mins_left = seconds / 60
    mins = mins_left % 60
    hours = mins_left / 60

    return "%.2d:%.2d:%.2d" % (hours, mins, secs)


def save_configuration(parameters):
    """Saves the current configuration to the .ini file
    """

    config = ConfigParser.ConfigParser()
    config_dir = os.path.join(os.path.expanduser("~"), '.mtvcgui')
    config_filename = os.path.join(config_dir, 'mtvcgui.ini')
    config.read(config_filename)

    if not config.has_section('mencoder GUI'):
        config.add_section('mencoder GUI')

    for parm in parameters.keys():
        if parm == 'channel_type':
            config.set('mencoder GUI', 'channel_type',
                       parameters.get('channel_type', 'number'))
        else:
            config.set('mencoder GUI', parm, parameters.get(parm))

    if not os.path.exists(config_dir):
        try:
            os.mkdir(config_dir)
        except:
            print "Error trying to create %s" % (config_dir, )

    try:
        config_file = open(config_filename, 'w')
        config.write(config_file)
        config_file.close()
    except:
        print "Error trying to save configuration to %s" % (config_filename, )


def generate_command(parameters, preview=False):
    """Generates a command for mencoder with current parameters.
    preview command generates a string to be displayed on screen, instead of
    a list of parameters for executing subprocess"""

    channel_type = parameters.get('channel_type', 'number')
    channel = parameters.get('channel')
    frequency = parameters.get('frequency')
    duration = parameters.get('duration')
    driver = parameters.get('driver')
    device = parameters.get('device')
    norm = parameters.get('norm')
    input = parameters.get('input')
    chanlist = parameters.get('chanlist')
    audiocodec = parameters.get('audiocodec')
    videocodec = parameters.get('videocodec')
    append_suffix = parameters.get('append_suffix')
    lavc_audiocodec = parameters.get('lavc_audiocodec')
    lavc_audiobitrate = parameters.get('lavc_audiobitrate')
    lame_audiobitrate = parameters.get('lame_audiobitrate')
    lavc_videocodec = parameters.get('lavc_videocodec')
    lavc_videobitrate = parameters.get('lavc_videobitrate')
    tvwidth = parameters.get('tvwidth')
    tvheight = parameters.get('tvheight')
    audiorate = parameters.get('audiorate')
    alsa_audio = parameters.get('alsa_audio')
    adevice = parameters.get('adevice')
    brightness = parameters.get('brightness')
    contrast = parameters.get('contrast')
    hue = parameters.get('hue')
    saturation = parameters.get('saturation')
    extratvparms = parameters.get('extratvparms')
    scaleheight = parameters.get('scaleheight')
    scalewidth = parameters.get('scalewidth')
    ofps = parameters.get('ofps')
    noskip = parameters.get('noskip')
    quiet = parameters.get('quiet')
    extrafilters = parameters.get('extrafilters')
    extramencoderparms = parameters.get('extramencoderparms')
    outputfile = parameters.get('outputfile')

    channel_text = parameters.get('channel_text')

    outputfile = make_filename(outputfile, channel_text,
                               append_suffix=append_suffix)


    if channel_type == 'frequency':
        tvparms = 'freq=' + frequency
    else:
        tvparms = 'channel=' + channel

    tvparms  += ':driver=' + driver
    tvparms += ':device=' + device

    if driver == 'v4l2':
        tvparms += ':normid=' + norm
    else:
        tvparms += ':norm=' + norm

    tvparms += ':input=' + input
    tvparms += ':chanlist=' + chanlist

    if tvwidth and tvheight:
        tvparms += ':width=' + tvwidth
        tvparms += ':height=' + tvheight

    if audiorate:
        tvparms += ':audiorate=' + audiorate

    if alsa_audio:
        tvparms += ":alsa"
        if adevice:
            tvparms += ":adevice=" + adevice


    if brightness:
        tvparms += ':brightness=' + brightness

    if contrast:
        tvparms += ':contrast=' + contrast

    if hue:
        tvparms += ':hue=' + hue

    if saturation:
        tvparms += ':saturation=' + saturation



    if extratvparms:
        tvparms += ':' + extratvparms

    mencoderparms = ['-tv']

    mencoderparms.append(tvparms)

    if audiocodec == 'none':
        mencoderparms.append('-nosound')
    else:
        mencoderparms += ['-oac', audiocodec]

    mencoderparms += ['-ovc', videocodec]

    if duration:
        mencoderparms += ['-endpos', duration]

    if ofps:
        mencoderparms += ['-ofps', ofps]

    if noskip:
        mencoderparms.append('-noskip')

    if quiet:
        mencoderparms.append('-quiet')


    if extrafilters or (scalewidth and scaleheight):
        filters = []
        if extrafilters:
            filters.append(extrafilters)
        if scaleheight:
            filters.append("scale=%s:%s" % (scalewidth, scaleheight) )

        filters = ','.join(filters)

        mencoderparms += ['-vf', filters]



    if lavc_audiocodec or lavc_audiobitrate or\
        lavc_videobitrate or lavc_videocodec:
        lavcopts = []
        if lavc_audiocodec:
            lavcopts.append("acodec=" + lavc_audiocodec)
        if lavc_audiobitrate:
            lavcopts.append("abitrate=" + lavc_audiobitrate)
        if lavc_videocodec:
            lavcopts.append("vcodec=" + lavc_videocodec)
        if lavc_videobitrate:
            lavcopts.append("vbitrate=" + lavc_videobitrate)

        lavcopts = ':'.join(lavcopts)

        mencoderparms += ['-lavcopts', lavcopts]

    if lame_audiobitrate:
        mencoderparms += ['-lameopts', 'cbr:br=' + lame_audiobitrate]


    if extramencoderparms:
        for extraparm in extramencoderparms.split(' '):
            mencoderparms.append(extraparm)

    mencoderparms += ['-o', outputfile]

    command = ['mencoder', 'tv://'] + mencoderparms

    if preview:
        return " ".join(command)
    else:
        return command


def generate_mplayer_command(parameters):
    """Generates a command for mplayer, for channel preview
    """

    channel_type = parameters.get('channel_type', 'number')
    channel = parameters.get('channel')
    frequency = parameters.get('frequency')
    driver = parameters.get('driver')
    device = parameters.get('device')
    norm = parameters.get('norm')
    input = parameters.get('input')
    chanlist = parameters.get('chanlist')
    tvwidth = parameters.get('tvwidth')
    tvheight = parameters.get('tvheight')
    extratvparms = parameters.get('extratvparms')
    audiorate = parameters.get('audiorate')
    alsa_audio = parameters.get('alsa_audio')
    adevice = parameters.get('adevice')
    brightness = parameters.get('brightness')
    contrast = parameters.get('contrast')
    hue = parameters.get('hue')
    saturation = parameters.get('saturation')
    scaleheight = parameters.get('scaleheight')
    scalewidth = parameters.get('scalewidth')
    ofps = parameters.get('ofps')
    extrafilters = parameters.get('extrafilters')


    channel_text = parameters.get('channel_text')

    if channel_type == 'frequency':
        tvparms = 'freq=' + frequency
    else:
        tvparms = 'channel=' + channel

    tvparms  += ':driver=' + driver
    tvparms += ':device=' + device

    if driver == 'v4l2':
        tvparms += ':normid=' + norm
    else:
        tvparms += ':norm=' + norm

    tvparms += ':input=' + input
    tvparms += ':chanlist=' + chanlist

    if tvwidth and tvheight:
        tvparms += ':width=' + tvwidth
        tvparms += ':height=' + tvheight

    if audiorate:
        tvparms += ':audiorate=' + audiorate

    if alsa_audio:
        tvparms += ":alsa"
        if adevice:
            tvparms += ":adevice=" + adevice

    if brightness:
        tvparms += ':brightness=' + brightness

    if contrast:
        tvparms += ':contrast=' + contrast

    if hue:
        tvparms += ':hue=' + hue

    if saturation:
        tvparms += ':saturation=' + saturation


    if extratvparms:
        tvparms += ':' + extratvparms

    mencoderparms = ['-tv']

    mencoderparms.append(tvparms)

    if ofps:
        mencoderparms += ['-fps', ofps]

    mencoderparms.append('-quiet')

    if extrafilters or (scalewidth and scaleheight):
        filters = []
        if extrafilters:
            filters.append(extrafilters)
        if scaleheight:
            filters.append("scale=%s:%s" % (scalewidth, scaleheight) )

        filters = ','.join(filters)

        mencoderparms += ['-vf', filters]

    return ['mplayer', '-slave', 'tv://'] + mencoderparms