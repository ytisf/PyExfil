#!/usr/bin/python

import os
import cv2
import sys
import time
import glob
import zlib
import base64
import hashlib
import zbarlight

from PIL import Image


# Globals
TEMP_NAME = "/tmp/random.png"
QR_DIR = "outputs"
DIR_MODE = "DIR_MODE"
CAM_MODE = "CAM_MODE"
DELIMITER = ";"
RAMP_FRAMES = 30  # Until camera light is adjusted


def _takesnapshot():
    def _take_image():
        retval, im = camera.read()
        return im

    camera = cv2.VideoCapture(0)

    for i in xrange(RAMP_FRAMES):
        temp = _take_image()

    camera_capture = _take_image()
    cv2.imwrite(TEMP_NAME, camera_capture)
    return True


def _decodePNG(filepath):
    if type(filepath) is not str:
        return False
    try:
        with open(filepath, "rb") as image_file:
            image = Image.open(image_file)
            image.load()
    except IOError, e:
        sys.stderr.write("Error %s while opening file '%s'.\n" % (e, filepath))
        return False
    try:
        codes = zbarlight.scan_codes("qrcode", image)
    except:
        return False
    return codes


def startFlow(mode):

    # Directory mode (reading QRs from file)
    if mode == DIR_MODE:
        file_data = {}
        file_name = ""
        file_md5 = ""
        amount_of_code = 0

        png_files = glob.glob(QR_DIR + "/*.png")
        for png in png_files:
            decoded = _decodePNG(png)

            if decoded is False or decoded is None:
                sys.stderr.write("Could not decode file '%s'.\n" % png)
                continue

            if png == QR_DIR + "/0.png":
                # Header file
                file_name, file_md5, amount_of_code = decoded[0].split(DELIMITER)
                amount_of_code = int(amount_of_code)
                continue

            counter = int(decoded[0][0:2])
            data = decoded[0][2:]
            file_data[counter] = data

        # Done with PNG analysis, now for decoding:
        raw = ""
        if int(counter) == amount_of_code:
            for key, val in file_data.items():
                raw += val
        try:
            rdata = base64.b64decode(raw)
        except:
            sys.stderr.write("Data failed Base64Decode.\n")
            return False
        try:
            rdata = zlib.decompress(rdata)
        except:
            sys.stderr.write("Data failed zlib decompression.\n")
            return False

        hexy = hashlib.md5(rdata).hexdigest()
        if hexy == file_md5:
            sys.stdout.write(
                "Success. File '%s' has been retrived with matching hashed.\n"
                % file_name
            )
        else:
            sys.stderr.write("Hashes do not match. Saving anyway.\n")

        f = open(file_name.replace("/", "_"), "wb")
        f.write(rdata)
        f.close()
        return True

    # Live mode. Capturing QRs from Webcam
    elif mode == CAM_MODE:
        sys.stdout.write("Hit Ctrl+C to stop listening.\n")
        while True:
            file_data = {}
            file_name = ""
            file_md5 = ""
            amount_of_code = 0
            try:
                _takesnapshot()
                temp = _decodePNG(TEMP_NAME)
                if temp is False or temp is None:
                    sys.stdout.write("No QR in image.\n")
                else:
                    sys.stdout.write("Got QR Code in image.\n")
                    try:
                        file_name, file_md5, amount_of_code = decoded[0].split(
                            DELIMITER
                        )
                        amount_of_code = int(amount_of_code)
                    except:
                        sys.stderr.write(
                            "There was an error reading the code as first package.\n.Please syncronize timing.\n"
                        )
                        continue

                    # First package was analyzed successfully.
                    counter = int(decoded[0][0:2])
                    data = decoded[0][2:]
                    file_data[counter] = data

                    raw = ""
                    if int(counter) == amount_of_code:
                        for key, val in file_data.items():
                            raw += val
                        try:
                            rdata = base64.b64decode(raw)
                        except:
                            sys.stderr.write("Data failed Base64Decode.\n")
                            return False
                        try:
                            rdata = zlib.decompress(rdata)
                        except:
                            sys.stderr.write("Data failed zlib decompression.\n")
                            return False

                        hexy = hashlib.md5(rdata).hexdigest()
                        if hexy == file_md5:
                            sys.stdout.write(
                                "Success. File '%s' has been retrived with matching hashed.\n"
                                % file_name
                            )
                        else:
                            sys.stderr.write("Hashes do not match. Saving anyway.\n")

                        f = open(file_name.replace("/", "_"), "wb")
                        f.write(rdata)
                        f.close()

                time.sleep(1)
            except KeyboardInterrupt:
                sys.stdout.write("\nGot a KeyboardInterrupt.\n")
                sys.exit(0)

    else:
        sys.stdout.write(
            "Mode selected is wrong. Choose either DIR_MODE or CAM_MODE.\n"
        )
        return False


if __name__ == "__main__":
    startFlow(mode=DIR_MODE)  # will use data in 'output' directory.
    startFlow(mode=CAM_MODE)  # will use data from camera
