from __future__ import print_function
import os
import wave
from struct import pack
from math import sin, pi
from random import randint
import fingerprint
import conf


WINDOW_SIZE = randint(1980, 2020)

k = WINDOW_SIZE / float(conf.AUDIO_FRAME_RATE)
K = conf.AUDIO_WINDOW_SIZE / float(conf.AUDIO_FRAME_RATE)

INTRO_DURATION = 30 * 6 * k
NOISE_DURATION = 10 * 8 * k

CLEAN_UP = True


def write_wave_file(filename, frames):

    fmt = '<{}h'.format(len(frames[0]))

    w = wave.open(filename, 'w')
    w.setparams((1, 2, 22050, 0, 'NONE', 'not compressed'))
    for frame in frames:
        w.writeframes(pack(fmt, *frame))

    w.close()


class Voice(object):

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


    @staticmethod
    def combine(voices):
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

    frames = []
    for _ in range(30):
        voices = (lambda: [Voice(55 + randint(0, 1200)) for _ in range(4)])()
        frames.extend([Voice.combine(voices) for _ in range(6)])

    return frames


def make_pseudo_noise():
    frames = []
    for _ in range(10):
        frames.extend([Voice.combine([Voice(55 + randint(0, 1200)) for __ in range(2)]) for _ in range(8)])
    return frames


def make_track(pattern, x=None):

    pattern = pattern.lower()
    if pattern.count('x') != 1:
        raise Exception("there must be one x!")

    if x is None:
        x = make_intro_track()

    track = []
    for ele in pattern:
        track += x if ele == 'x' else make_pseudo_noise()

    return track


def make_test_cases(n):

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


if __name__ == '__main__':

    TEST_INTRO = 'test_intro.wav'
    TEST_TRACK = 'test_track{}.wav'

    N_TEST_CASES = 8

    intro = make_track('x')
    write_wave_file(TEST_INTRO, intro)
    fp = fingerprint.make_fingerprint(TEST_INTRO)

    test_cases = make_test_cases(N_TEST_CASES)

    print("tracks:")
    print('\n'.join([t['pattern'] for t in test_cases]))
    print("intro duration", INTRO_DURATION)
    print("noise duration", NOISE_DURATION)

    for test in test_cases:
        match = fingerprint.find_fingerpint_in_file(fp, TEST_TRACK.format(test['i']))
        test['actual'] = K * match[0]
        print('{}\t{:6d}\t{}\t{:6.2f}\t{:6.2f}'.format(test['i'], match[0], match[1], test['actual'], test['expected']))

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
