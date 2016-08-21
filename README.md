# python-introcutter
A simple program to cut the intro out of tv series episodes

Problem: you've just (very legally) downloaded the new season of your favourite tv show and you're about to binge whatch it, but, you get really annoyed when you have to whatch the intro every time.

Solution: open one episode, take note of starting time and duration of the intro, insert the value in the script and run it, it'll generate a copy of all the episodes without the intro.

prerequesites: 
- python 2.7 (maybe works with python 3 who knows...)
- numpy
- ffmpeg installed systemwise or executable as stand alone

tested with python 2.7 and ffmpeg 2.8.6-1ubuntu2 on ubuntu 16.04 with futurama and stranger things

before running [main.py](https://github.com/lelloman/python-introcutter/blob/master/main.py), you need to set some values in [conf.py](https://github.com/lelloman/python-introcutter/blob/master/conf.py)
- ```TMP_DIR``` a dir to store temporary files, all files in this dir will be deleted at the end
- ```INTRO_VIDEO_FILE``` path to the file from which copy the intro song
- ```INTRO_START_S``` the starting time in seconds of the intro song in ```INTRO_VIDEO_FILE```
- ```INTRO_DURATION_S``` duration in seconds of the intro song
- ```INPUT_DIR``` path to the directory where your videos are located, it will cut the intro out of all of them
- ```OUTPUT_DIR``` path of the directory where cut video will be saved
- ```FFMPEG``` if you can run ffmpeg (same for ```FFPROBE```) just with ```ffmpeg``` command, the default is fine, otherwise you need to provide the command to execute ffmpeg (and ffprobe)
