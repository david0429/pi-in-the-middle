#!/usr/bin/env python

# Simple test script that plays (some) wav files

from __future__ import print_function

import sys
import time
import wave
import getopt
import alsaaudio


def play(device, f):
    micVol = 56
    speakerVolume = 46

    print('%d channels, %d sampling rate\n' % (f.getnchannels(),
                                               f.getframerate()))
    mic = alsaaudio.Mixer("Mic")
    for i in range (56):
        micVol = micVol - 1
        mic.setvolume(micVol)
        time.sleep(0.05)

    speakers = alsaaudio.Mixer("Headphone")
    speakers.setvolume(speakerVolume)

    # Set attributes
    device.setchannels(f.getnchannels())
    device.setrate(f.getframerate())

    # 8bit is unsigned in wav files
    if f.getsampwidth() == 1:
        device.setformat(alsaaudio.PCM_FORMAT_U8)
    # Otherwise we assume signed data, little endian
    elif f.getsampwidth() == 2:
        device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    elif f.getsampwidth() == 3:
        device.setformat(alsaaudio.PCM_FORMAT_S24_3LE)
    elif f.getsampwidth() == 4:
        device.setformat(alsaaudio.PCM_FORMAT_S32_LE)
    else:
        raise ValueError('Unsupported format')

    periodsize = f.getframerate() / 8

    device.setperiodsize(periodsize)

    currentVolume = 0
    played = 0
    data = f.readframes(periodsize)
    while data:
        speakers.setvolume(int(currentVolume / 2.0))
        if played - 12 < speakerVolume * 2 and played - 12 >= 0:
            currentVolume = currentVolume + 1
        if 120 - played <= speakerVolume * 2:
            currentVolume = currentVolume - 1

        device.write(data)
        played = played + 1
        data = f.readframes(periodsize)
        if played >= 120:
            break

    speakers.setvolume(0)
    time.sleep(0.8)
    speakers.setvolume(speakerVolume)

    micVol = 0
    for i in range (56):
        micVol = micVol + 1
        mic.setvolume(micVol)
        time.sleep(0.05)

def usage():
    print('usage: playwav.py [-d <device>] <file>', file=sys.stderr)
    sys.exit(2)

if __name__ == '__main__':

    device = 'default'

    opts, args = getopt.getopt(sys.argv[1:], 'd:')
    for o, a in opts:
        if o == '-d':
            device = a

    if not args:
        usage()
        
    f = wave.open(args[0], 'rb')
    device = alsaaudio.PCM(device=device)

    play(device, f)

    f.close()
