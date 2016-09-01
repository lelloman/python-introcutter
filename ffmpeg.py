"""
A set of functions that wrap useful ffmpeg commands
"""

import string
import re
from random import choice
from subprocess import check_call, Popen, PIPE
from conf import *


def make_tmp_filename(file_for_ext=''):
    """
    generate a random filename to be used in the tmp directory

    :param file_for_ext: a filename from which eventually copy the extension
    :return: the full path of a file in tmp directory
    """
    return os.path.join(TMP_DIR, ''.join([choice(string.lowercase) for _ in range(24)]))\
        + (ext(file_for_ext) if file_for_ext else '')


def ext(filename):
    """
    :param filename: a file name with extension e.g. movie.mkv
    :return: the extension of the filename e.g. .mkv
    """
    return '.' + filename.split('.')[-1]


def extract_video_chunk(source_file, dst_file, start_s, duration_s):
    """
    extract a chunk of a video at the given position and save it to file

    :param source_file: path of the source video file
    :param dst_file: path of the file to be created
    :param start_s: starting point of the chunk in seconds
    :param duration_s: duration of the chunk in seconds
    :return: path of the file to be created
    """
    check_call([
        FFMPEG,
        '-i', source_file,
        '-ss', str(start_s),
        '-t', str(duration_s),
        '-c', 'copy',
        dst_file], stdout=STD_OUT, stderr=STD_OUT)
    return dst_file


def extract_audio(source_file, dst_file, sample_rate=AUDIO_FRAME_RATE):
    """
    extract the audio from a media file and save it into a wav file

    :param source_file: the path of the video to extract the audio from
    :param dst_file: the path of the audio file to be created
    :param sample_rate: the sample rate of the output audio file
    :return: the path of the output file
    """
    check_call([
        FFMPEG, '-i', source_file,
        '-acodec', 'pcm_s16le',
        '-ar', str(sample_rate),
        '-ac', '1',
        dst_file], stdout=STD_OUT, stderr=STD_OUT)
    return dst_file


def extract_audio_chunk(source_file, dst_file, start_s, duration_s, sample_rate=AUDIO_FRAME_RATE):
    """
    given a position and a duration, create an audio file from a given video

    :param source_file: path of the source video
    :param dst_file: path of the audio file to be created
    :param start_s: starting point of the chunk in seconds
    :param duration_s: duration of the chunk in seconds
    :param sample_rate: sample rate of the generated audio file
    :return: path of the audio file to be created
    """
    chunk = make_tmp_filename() + ext(source_file)
    extract_video_chunk(source_file, chunk, start_s, duration_s)
    extract_audio(chunk, dst_file, sample_rate=sample_rate)
    os.remove(chunk)
    return dst_file


def get_video_duration(filename):
    """
    parse the output of ffprobe to get the duration of a video

    :param filename: path of the target video
    :return: duration in seconds of the video
    """
    p = Popen([FFPROBE, '-i', filename, '-show_format'], stdout=PIPE, stderr=PIPE)
    return float(re.findall(r'.*duration=([0-9.]+)\D', p.stdout.read())[0])


def concat_videos(source_file1, source_file2, dst_file):
    """
    create a video file concatenating 2 videos

    :param source_file1: first video path
    :param source_file2: second video path
    :param dst_file: output file path
    :return: output file path
    """

    # ffmpeg concat expect a text file with all the video files
    tmp = make_tmp_filename()
    with open(tmp, 'w') as f:
        f.write("file '{}'\nfile '{}'".format(source_file1, source_file2))

    check_call([FFMPEG, '-f', 'concat', '-i', tmp, '-c', 'copy', dst_file], stdout=STD_OUT, stderr=STD_OUT)


def remove_chunk_from_video(source_file, dst_file, start_s, duration_s):
    """
    create a video that is a copy of the original but cut out a chunk
    at the given position

    :param source_file: the path of the source video
    :param dst_file: the path of the video to be created
    :param start_s: the starting time of the chunk to be cut out in seconds
    :param duration_s: the duration in seconds of the chunk to cut
    :return: the path of the output file
    """

    duration = get_video_duration(source_file)
    part1 = make_tmp_filename() + ext(source_file)
    part2 = make_tmp_filename() + ext(source_file)

    extract_video_chunk(source_file, part1, 0, start_s)
    extract_video_chunk(source_file, part2, int(start_s + duration_s), int(duration))

    if os.path.isfile(dst_file):
        os.remove(dst_file)

    concat_videos(part1, part2, dst_file)
