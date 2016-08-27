#!/usr/bin/python
"""
main routine of the intro cutter.

1 - extract a wav file with the intro from the given video,
    position and duration must be known and set in conf.py
2 - make a fingerprint from the extracted wav file
3 - iterate all video files in the given directory
    3a - extract first half of the audio track of the video,
        the intro is not gonna be in the seconds half, right?
    3b - look for the position in the audio track that best match the fingerprint
    3c - create a new video file cutting out the matched position + duration
4 - log and clean up

"""
from __future__ import print_function
import os
from fingerprint import make_fingerprint, find_fingerprint_in_file
from ffmpeg import make_tmp_filename as tmp, ext, extract_audio_chunk, get_video_duration, remove_chunk_from_video
from conf import *


# extract the audio of the intro and make a fingerprint of it
intro_wav = extract_audio_chunk(INTRO_VIDEO_FILE, tmp() + '.wav', INTRO_START_S, INTRO_DURATION_S)
fp = make_fingerprint(intro_wav)

k = AUDIO_FRAME_RATE / float(AUDIO_WINDOW_SIZE)
fp_duration_seconds = len(fp) / k

# iterate all video file
log = ''
for video in os.listdir(INPUT_DIR):
    if ext(video)[1:].lower() not in VIDEO_EXT:
        continue

    # extract the audio only for the first half of the video
    duration = get_video_duration(os.path.join(INPUT_DIR, video)) / 2
    target_wav = extract_audio_chunk(os.path.join(INPUT_DIR, video), tmp() + ".wav", 0, duration)

    # compare the fingerprint with the audio extracted from the video
    match = find_fingerprint_in_file(fp, target_wav)
    log += 'index {:9} - value {:18} {:06.2f}s - {}\n'.format(match[0], match[1], match[0] / k, video)

    input_video = os.path.join(INPUT_DIR, video)
    output_video = os.path.join(OUTPUT_DIR, OUTPUT_PREFIX+video)
    remove_chunk_from_video(input_video, output_video, int(match[0] / k), fp_duration_seconds)

with open('log.txt', 'w') as f:
    f.write(log)
print(log)

if CLEAN_TMP:
    for ele in os.listdir(TMP_DIR):
        os.remove(os.path.join(TMP_DIR, ele))
