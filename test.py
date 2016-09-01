#!/usr/bin/python
"""
a simple test to check that every piece is in place

TMP_DIR and OUTPUT_DIR from conf.py are used in order to check that
writing there is ok

first a mock intro track is created, just some random tones put together,
then N_TEST_CASES tracks are created, they will contain the intro at different
positions while the rest of the file will be other random tones.

all the test tracks are then matched against the mock intro and the expected results
evaluated, the tracks are made of chunks that can be either the intro ('x') or some other
random tones ('-') so that they look like this:
track 0 x-------
track 1 -x------
track 2 --x-----
...

therefore match values should be something like this:
track	index	match v		actual		expected
0	        0	46464	    0.00	    0.00
1	       77	22631	    7.15	    7.28
2	      156	24357	   14.49	   14.56
...
"""
from __future__ import print_function
import os
import wave
from struct import pack
from math import sin, pi
from random import randint
import fingerprint
import conf


# something around 10 should be ok
N_TEST_CASES = 8

# the size of this is different from the one used for the fft
WINDOW_SIZE = randint(1980, 2020)

# convert test frames into seconds
k = WINDOW_SIZE / float(conf.AUDIO_FRAME_RATE)

# convert matched frame index into seconds
K = conf.AUDIO_WINDOW_SIZE / float(conf.AUDIO_FRAME_RATE)

INTRO_DURATION = 30 * 6 * k
NOISE_DURATION = 10 * 8 * k

CLEAN_UP = True

TEST_INTRO = os.path.join(conf.TMP_DIR, 'test_intro.wav')
TEST_TRACK = os.path.join(conf.OUTPUT_DIR, 'test_track{}.wav')


def write_wave_file(filename, frames):
    """
    create a wave file from a list of pcm windows

    :param filename: wave file to be created
    :param frames: a list of pcm windows
    """

    fmt = '<{}h'.format(len(frames[0]))

    w = wave.open(filename, 'w')
    w.setparams((1, 2, conf.AUDIO_FRAME_RATE, 0, 'NONE', 'not compressed'))
    for frame in frames:
        w.writeframes(pack(fmt, *frame))

    w.close()


class Voice(object):
    """
    given a frequency, it can generate frames of a
    sin wave keeping track of the phase
    """

    amplitude = (2 ** 15) * .4

    def __init__(self, freq):
        self.freq = freq
        self.k = (freq / 22050.) * 2 * pi
        self.fi = 0

    def get_window(self):
        return [sin(self.phase() * self.k) for _ in range(WINDOW_SIZE)]

    def phase(self):
        self.fi += 1
        return self.fi


def combine_voices(voices):
    """
    sum a list of pcm window with clipping

    :param voices: a list of pcm windows
    :return: a pcm window
    """
    f = [0 for _ in range(WINDOW_SIZE)]
    max_f = (2 ** 15) - 1000
    min_f = -max_f
    for v in voices:
        frame = v.get_window()
        for i in range(WINDOW_SIZE):
            f[i] += frame[i]

    for i in range(WINDOW_SIZE):
        fi = f[i] * Voice.amplitude
        if fi > max_f:
            fi = max_f
        elif fi < min_f:
            fi = min_f
        f[i] = int(fi)

    return f


def make_intro_track():
    """
    create a mock intro track, a bunch of random tones
    :return: a list of pcm frames
    """
    frames = []
    for _ in range(30):
        voices = (lambda: [Voice(55 + randint(0, 1200)) for _ in range(4)])()
        frames.extend([combine_voices(voices) for _ in range(6)])

    return frames


def make_pseudo_noise_track():
    """
    create a non intro pcm window, a bunch of random tones
    :return: a list of pcm frames
    """
    frames = []
    for _ in range(10):
        frames.extend([combine_voices([Voice(55 + randint(0, 1200)) for _ in range(2)]) for _ in range(8)])
    return frames


def make_track(pattern, x=None):
    """
    create a pcm track, the format of the input should look like
    '--x----' where x is the intro and - is non intro window.
    if an intro x is passed it will be used otherwise it will generate
    a random one

    :param pattern: a string like -x--
    :param x: the intro track as pcm frames list
    :return: a big list of pcm frames
    """
    pattern = pattern.lower()
    if pattern.count('x') != 1:
        raise Exception("there must be one x!")

    if x is None:
        x = make_intro_track()

    track = []
    for ele in pattern:
        track += x if ele == 'x' else make_pseudo_noise_track()

    return track


def make_test_cases(n, intro):
    """
    create a list of test cases to test the script,
    each test case is a dictionary with keys:
    'i': the index of the element
    'track': the test track as a pcm frames list
    'pattern': a string like -x---
    'expected': the position of the intro in seconds

    :param n: number of test cases to create
    :param intro: the intro track to put in the test track
    :return: a list of test case dictionaries
    """
    patterns = [('-' * i) + 'x' + ('-' * ((N_TEST_CASES - 1) - i)) for i in range(n)]

    test_cases = [
        {
            'dummy': print('make track {} of {}'.format(i + 1, N_TEST_CASES)),
            'track': make_track(x, intro),
            'pattern': x,
            'i': i,
            'expected': NOISE_DURATION * i
        }
        for i, x in enumerate(patterns)
        ]

    for i, test_case in enumerate(test_cases):
        print("writing wave file", i+1, "of", len(test_cases), "...")
        write_wave_file(TEST_TRACK.format(i), test_case['track'])

    return test_cases


def run_test():

    intro = make_track('x')
    write_wave_file(TEST_INTRO, intro)
    fp = fingerprint.make_fingerprint(TEST_INTRO)

    test_cases = make_test_cases(N_TEST_CASES, intro)

    print("tracks:")
    print('\n'.join([t['pattern'] for t in test_cases]))
    print("intro duration", INTRO_DURATION)
    print("noise duration", NOISE_DURATION)

    print('track\tindex\tmatch v\t\tactual\t\texpected')
    for test in test_cases:
        match = fingerprint.find_fingerprint_in_file(fp, TEST_TRACK.format(test['i']))
        test['actual'] = K * match[0]
        print('{}\t{:9d}\t{}\t{:8.2f}\t{:8.2f}'.format(test['i'], match[0], match[1], test['actual'], test['expected']))

    if CLEAN_UP:
        os.remove(TEST_INTRO)
        for i in range(len(test_cases)):
            os.remove(TEST_TRACK.format(i))

    ok = True
    for test in test_cases:
        if abs(test['expected'] - test['actual']) > 1.:
            ok = False
            print("<!!!> expected value for track {} was {} but got {}".format(test['i'], test['expected'], test['actual']))

    print("OK!" if ok else "")


if __name__ == '__main__':
    run_test()
