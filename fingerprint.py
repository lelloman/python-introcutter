"""
A set of function to create and compare fingerprints
"""
from wavewrap import WaveWrap


def make_fingerprint(wave_filename):
    """
    create a fingerprint from a wav file, it consists
    of a list of the loudest frequencies for each frame
    of the audio file. also saved it to file

    :param wave_filename: path of the source wav file
    :param dst_filename: path of the file to save the fp
    :return: the generated fp
    """
    w = WaveWrap(wave_filename)

    fp = []
    while w.has_next():
        fp.append(sorted(w.next_freq_window()))

    return fp


def compare_fingerprints(fp1, fp2):
    """
    compute the 'distance' between two fingerprints.
    it consists of the sum of the distance of each frame
    of fp1 from the frame at the same index in fp2.
    since each frame is a sorted list of frequencies, the
    distance between two frames is the sum of the |difference|
    of the values at the same indices in both frames

    :param fp1: a fingerprint (list)
    :param fp2: a fingerprint (list)
    :return: the difference between fp1 fp2 (int)
    """
    s = 0
    x = min(len(fp1), len(fp2))
    y = min(len(fp1[0]), len(fp2[0]))

    for i in range(x):
        t1 = fp1[i]
        t2 = fp2[i]

        for j in range(y):
            s += abs(t1[j] - t2[j])

    return s


def find_fingerpint_in_file(fp, target_filename):
    """
    given a fingerprint and an audio file, it search the position
    in the audio file with the highest similarity with the fingerprint

    :param fp: the fingerprint used to compute the match
    :param target_filename: path of the audio file
    :return: a tuple with the index of the best match and its value
    """

    target = WaveWrap(target_filename)

    target_buffer = [target.next_freq_window() for _ in range(len(fp))]

    min_score = 2 ** 128
    min_index = -1
    i = 0
    while target.has_next():

        target_buffer.pop(0)
        target_buffer.append(target.next_freq_window())

        score = compare_fingerprints(fp, target_buffer)

        if score < min_score:
            min_score = score
            min_index = i

        i += 1

    return min_index, min_score

