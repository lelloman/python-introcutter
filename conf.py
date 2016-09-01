import sys
import os


# frame rate that will be used for all wav files
AUDIO_FRAME_RATE = 22050
# number of pcm frames for fft window
AUDIO_WINDOW_SIZE = 2048
# extensions to look for inside the input directory
VIDEO_EXT = ['avi', 'mkv', 'flv', 'wmv', 'mp4', 'm4v', 'mpeg', 'mpg']


# place to store trash
TMP_DIR = '/home/lelloman/PycharmProjects/intro-cutter/tmp'
# since i'm using a common folder it's better to clean it
CLEAN_TMP = True
# hide ffmpeg command output from terminal
VERBOSE = False
STD_OUT = sys.stdout if VERBOSE else open(os.devnull, 'w')
STD_ERR = sys.stderr if VERBOSE else open(os.devnull, 'w')

# command to invoke ffmpeg
FFMPEG = 'ffmpeg'
# command to invoke ffprobe
FFPROBE = 'ffprobe'


# the path of the video to extract the intro
INTRO_VIDEO_FILE = '/home/lelloman/Downloads/Futurama Season 1/Futurama [1x01] The Space Pilot 3000.avi'
# starting position in seconds of the intro in the given video
INTRO_START_S = 180
# duration in seconds of the intro
INTRO_DURATION_S = 27


# all videos found here will be converted
INPUT_DIR = '/home/lelloman/Downloads/Futurama Season 2 (copy)'
# place to store all new videos without intro
OUTPUT_DIR = '/home/lelloman/PycharmProjects/intro-cutter/output'
# rename new files with this string + the old name
OUTPUT_PREFIX = 'nointro_'

