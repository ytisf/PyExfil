#!/usr/bin/python
from __future__ import division  # Avoid division problems in Python 2
import sys
import wave
import math
import zlib
import base64
import pyaudio
import numpy as np

PyAudio = pyaudio.PyAudio
BITRATE = 14400
RATE = 16000

# Todo: Complete the listener for WAV and Microphone usage
#
# class GetEmBoy():
#     def __init__(self, wav_file):
#         self.wave_file = wav_file
#
#         self.stream = None
#
#     def _getWave(self):
