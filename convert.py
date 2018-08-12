#!/bin/python

# author: andyzhshg@gmail.com
# date: 2018.08.12

# This script using ffmpeg to add an aac/ac3 audio stream 
# to a video only has eac3 audio stream. 

# This make videos can be played on devices 
# which can not decode eac3 audios. 

import os
import json
import subprocess
import sys
import datetime
import shutil

def PrintLog(message, file, level = 'info'):
    now = datetime.datetime.now()
    print >> file, "[%s][%s] %s" %(str(now), level, message)

def ExtractAudioStreams(ffprobe_path, video_path):
    '''
    extract all audio streams from video by ffprobe
    '''
    try:
        meta_str = subprocess.check_output([ffprobe_path, '-v', 'quiet', '-print_format', 'json', '-show_streams', '-i', video_path])
        meta = json.loads(meta_str)
        audios = []
        for stream in meta['streams']:
            if stream['codec_type'] == 'audio':
                index = stream['index']
                codec = stream['codec_name']
                bitrate = 384000 # default bitrate if not find
                if stream.has_key('tags'):
                    tags = stream['tags']
                    bps = bitrate
                    if tags.has_key('BPS'):
                        bps = int(tags['BPS'])
                    bps_eng = bitrate
                    if tags.has_key('BPS-eng'):
                        bps_eng = int(tags['BPS-eng'])
                    if bps != bitrate:
                        bitrate = bps
                    if bps_eng != bitrate:
                        bitrate = bps_eng 
                audios.append({
                    'index': index,
                    'codec': codec,
                    'bitrate': bitrate 
                })
        return audios
    except:
        return []


def NeedConvert(audio_streams, unsupportd_codecs):
    '''
    check if video only has audio streams not supported
    return -1 if not need convert
    return index of audio stream to be converted if need convert
    '''
    index = -1
    bitrate = 0
    cnt = -1
    for stream in audio_streams:
        cnt += 1
        codec = stream['codec'].lower()
        if codec not in unsupportd_codecs:
            return -1
        if stream['bitrate'] >= bitrate:
            bitrate = stream['bitrate']
            index = cnt
    return index

def ConvertAudio(ffmpeg_path, video_path, stream_info, audio_codec, max_bitrate, audio_path):
    '''
    convert audio stream to supported codec
    '''
    audio_index = stream_info['index']
    bitrate = stream_info['bitrate']
    if bitrate > max_bitrate:
        bitrate = max_bitrate
    try:
        subprocess.check_output([
            ffmpeg_path, 
            '-threads', '2',
            '-loglevel', 'panic',
            '-y',
            '-i', video_path, 
            '-map', '0:' + str(audio_index), 
            '-acodec', audio_codec, 
            # '-b:a', str(bitrate), 
            audio_path
        ])
        return True
    except:
        return False

def AssembleVideo(ffmpeg_path, video_path, audio_path, out_path):
    '''
    assemble conmverted audio to origin viodeo
    '''
    try:
        subprocess.check_output([ffmpeg_path, '-loglevel', 'panic', '-y', '-i', video_path, '-i', audio_path, '-map', '0', '-map', '1', '-codec', 'copy', out_path])
        return True
    except:
        return True

def Main():
    if len(sys.argv) != 2:
        print 'Usage: python %s path_of_video_to_convert' %(sys.argv[0])
        sys.exit(-1)
    ffprobe = '/usr/bin/ffprobe'
    ffmpeg = '/usr/bin/ffmpeg'
    unsupportd_codecs = ['eac3']
    tmp_path = '/tmp'
    log_path = sys.stdout
    convert_to_codec = 'ac3'
    max_bitrate = 640000
    keep_origin = False
    if os.environ.has_key('FFPROBE_PATH'): 
        ffprobe = os.environ['FFPROBE_PATH']
    if os.environ.has_key('FFMPEG_PATH'):
        ffmpeg = os.environ['FFMPEG_PATH']
    if os.environ.has_key('UNSUPPORT_CODECS'):
        unsupportd_codecs = os.environ['UNSUPPORT_CODECS'].split(';')
    if os.environ.has_key('TMP_PATH'):
        tmp_path = os.environ['TMP_PATH']
    if os.environ.has_key('LOG_PATH'):
        log_path = open(os.environ['LOG_PATH'], 'w')
    if os.environ.has_key('CONVERT_TO_CODEC'):
        convert_to_codec = os.environ['CONVERT_TO_CODEC']
    if os.environ.has_key('MAX_BITRATE'):
        max_bitrate = int(os.environ['MAX_BITRATE'])
    if os.environ.has_key('KEEP_ORIGIN'):
        if str(os.environ['KEEP_ORIGIN']) == '1':
            keep_origin = True
    video_path = sys.argv[1]
    audios = ExtractAudioStreams(ffprobe, video_path)
    if len(audios) == 0:
        PrintLog('ffprobe run fail on file: ' + video_path, log_path, 'warning')
        sys.exit(-1)
    audio_index = NeedConvert(audios, unsupportd_codecs)
    if audio_index < 0:
        PrintLog('do not need covert: ' + video_path, log_path)
        sys.exit(1)
    audio_path = tmp_path + '/audio.' + convert_to_codec
    if not ConvertAudio(ffmpeg, video_path, audios[audio_index], convert_to_codec, max_bitrate, audio_path):
        PrintLog('convert audio to %s fail: %s' %(convert_to_codec, video_path), log_path, 'warn')
        sys.exit(-2)
    out_path = video_path[:video_path.rfind('.')] + '.' + convert_to_codec + video_path[video_path.rfind('.'):]
    if not AssembleVideo(ffmpeg, video_path, audio_path, out_path):
        PrintLog('assemble video fail: ' + out_path, log_path, 'warn')
    if not keep_origin:
        try:
            os.remove(audio_path)
            os.rename(out_path, video_path)
        except:
            PrintLog('fail to move %s to %s' %(out_path, video_path), log_path, 'warn')
    PrintLog('[success] ' + video_path, log_path)
    sys.exit(0)

if __name__ == '__main__':
    Main()
