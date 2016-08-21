import wave
import numpy as np
from struct import unpack
from conf import AUDIO_WINDOW_SIZE


class WaveWrap(object):
    """
    a simple class that wraps a wav file, it can read chunks of it, transform them
    into frequency domain and select the loudest frequencies
    """
    def __init__(self, filename, window_size=AUDIO_WINDOW_SIZE, unpack_fmt="<{}h"):
        """
        :param filename: path to the wav file
        :param window_size: size in frames of the fft window
        :param unpack_fmt: struct format of a pcm frame, default is signed 16bits le
        """
        self.wave_file = wave.open(filename, 'r')
        self.length = self.wave_file.getnframes()
        self.window_size = window_size
        self.unpack_fmt = unpack_fmt.format(self.window_size)

        # compute the frequency of each fft bin
        self.freq = np.fft.fftfreq(window_size, d=1. / self.wave_file.getframerate()).astype(int)

        # the position of the next window to read
        self.cursor = 1
        self.n_windows = self.length / window_size

        print "WaveWrap<{}> length {}".format(filename, self.length)

    def has_next(self):
        """
        :return: if it's safe to read the next window
        """
        return self.cursor < self.n_windows

    def next_pcm_window(self):
        """
        :return: next pcm window
        """
        try:
            wave_data = self.wave_file.readframes(self.window_size)
        except Exception as e:
            print e.message
            wave_data = np.zeros(self.window_size)
        self.cursor += 1
        return unpack(self.unpack_fmt, wave_data)

    def next_fft_window(self):
        """
        :return: magnitude of fft of the next pcm window
        """
        return np.abs(np.fft.rfft(self.next_pcm_window()))

    def next_indices_window(self, n_indices=5):
        """
        :param n_indices: number of best indices to pick
        :return: list of the indices of the loudest frequency bin in next window
        """
        return np.argpartition(self.next_fft_window(), -n_indices)[-n_indices:]

    def next_freq_window(self, n_indices=5):
        """
        :param n_indices: number of best indices to pick
        :return: list of the loudest frequencies in the next window
        """
        return sorted([self.freq[e] for e in self.next_indices_window(n_indices)])
