#!/usr/bin/python
import sys
import zlib
import hashlib
import binascii

import numpy as np
from PIL import Image


# Globals
BUFF_CHAR = 5
PIXEL_MAX = 255
MODES = ['baseimage', 'encode', 'decode']


def _str2bin(raw_data):
    return str(bin(int(binascii.hexlify(raw_data), 16)))[2:]


def file2array(file_name):
    """
    Will covert file name to a 3xlen array of the binary data
    """
    try:
        f = open(file_name, 'rb')
        st = f.read()
        f.close()
    except IOError, e:
        sys.stderr.write("\t[!] Cannot open the file '%s'.\n" % file_name)
        return False

    data = zlib.compress(st)
    sys.stdout.write("\t[.] Size before compression is %s.\n" % len(st))
    sys.stdout.write("\t[.] Size after compression is %s.\n" % len(data))
    sys.stdout.write("\t[.] Compression ratio of %s.\n" %
                     (len(data) / len(st)))
    bin_data = _str2bin(data)
    n = 3
    split_by_3 = [bin_data[i:i + n] for i in range(0, len(bin_data), n)]

    retMe = []
    for item in split_by_3:
        n = 1
        item = [item[i:i + n] for i in range(0, len(item), n)]
        try:
            retMe.append([int(item[0]), int(item[1]), int(item[2])])
        except:
            try:
                retMe.append([int(item[0]), int(item[1]), BUFF_CHAR])
            except:
                retMe.append([int(item[0]), BUFF_CHAR, BUFF_CHAR])

    return retMe


def decode_data(arrToDecode):
    main = ""
    for data in arrToDecode:
        r, g, b = data
        a = chr(int(str(r) + str(g) + str(b)))
        main += a
    return zlib.decompress(main)


def openImage(image_path):
    # Open Image
    img = Image.open(image_path)
    ImageWidth, ImageHeight = img.size
    TotalPixels = ImageWidth * ImageHeight
    return img, ImageWidth, ImageHeight, TotalPixels


def image2pixelarray(imgObj):
    arr = np.array(imgObj)
    pixels = list(imgObj.getdata())
    return pixels


def get_file_content(path):
    f = open(path, 'rb')
    exfilMe = f.read()
    f.close()
    return exfilMe


def CreateExfiltrationFile(originalImage, rawData, OutputImage):
    sys.stdout.write("\nStarting Encoding Process\n")
    sys.stdout.write("-" * len("Starting Encoding Process") + "\n")
    img, ImageWidth, ImageHeight, TotalPixels = openImage(originalImage)
    pixels = image2pixelarray(img)
    arrayToEncorprate = file2array(rawData)
    if len(arrayToEncorprate) >= TotalPixels:
        sys.stderr.write(
            "\t[!] The size of data is bigger then the amount of pixels!\n")
        sys.stderr.write("\t[!] Size of pixels is %s and size of encoded data is %s.\n" % (
            len(arrayToEncorprate), TotalPixels))
        exit()

    FinalPixels = []
    offset = 0

    for pixel in pixels:
        if 255 == pixel[0]:
            sys.stderr.write(
                "\t[!] You have choosen an image with absolute colours. Please choose another image.\n")
            sys.exit(1)
        if 255 == pixel[1]:
            sys.stderr.write(
                "\t[!] You have choosen an image with absolute colours. Please choose another image.\n")
            sys.exit(1)
        if 255 == pixel[2]:
            sys.stderr.write(
                "\t[!] You have choosen an image with absolute colours. Please choose another image.\n")
            sys.exit(1)

    sys.stdout.write("\t[.] Will now encorporate %s bits into the image with total pixels of %s.\n" % (
        len(arrayToEncorprate), TotalPixels))
    for i in range(0, len(arrayToEncorprate)):
        AddRed, AddGreen, AddBlue = arrayToEncorprate[i]
        FinalPixels.append(
            (
                int(pixels[i][0]) + int(AddRed),
                int(pixels[i][1]) + int(AddGreen),
                int(pixels[i][2]) + int(AddBlue)
            )
        )

    padding_length = TotalPixels - len(arrayToEncorprate)
    sys.stdout.write("\t[.] Will now incorporate %s bits of padding.\n" % (
        TotalPixels - len(arrayToEncorprate)))
    for i in range(TotalPixels - padding_length, TotalPixels):
        FinalPixels.append(
            (
                int(pixels[i][0]) + BUFF_CHAR,
                int(pixels[i][1]) + BUFF_CHAR,
                int(pixels[i][2]) + BUFF_CHAR
            )
        )

    total_data_length = padding_length + len(arrayToEncorprate)
    sys.stdout.write("\t[+] Total of %s bits of data + %s bits of padding for a total of %s bits.\n" %
                     (len(arrayToEncorprate), padding_length, total_data_length))

    im2 = Image.new(img.mode, (ImageWidth, ImageHeight))
    im2.putdata(FinalPixels)
    open(OutputImage, 'wb').write("\x00") # Touching file as PIL does an append...
    im2.save(OutputImage)
    sys.stdout.write("\t[+] New image saved at '%s'.\n\n" % OutputImage)


def DecodeExfiltrationFile(originalImage, newImage, outputPath):
    sys.stdout.write("\nStarting Decoding Process\n")
    sys.stdout.write("-" * len("Starting Decoding Process") + "\n")
    img, ImageWidth, ImageHeight, TotalPixels = openImage(originalImage)
    originalPixels = image2pixelarray(img)
    sys.stdout.write(
        "\t[+] Loaded image '%s' as original reference image.\n" % originalImage)

    nImage, newImageWidth, newImageHeight, newTotalPixels = openImage(newImage)
    newPixels = image2pixelarray(nImage)
    sys.stdout.write("\t[+] Loaded image '%s' as secret image.\n" % newImage)

    if TotalPixels != newTotalPixels:
        sys.stderr.write("\t[!] Size of reference image is %sx%s while secret image size is %sx%s.\n" % (
            ImageWidth, ImageHeight, newImageWidth, newImageHeight))
        return False

    diff = []
    for i in range(0, len(newPixels)):
        try:
            originalRed, originalGreen, originalBlue, a = originalPixels[i]
        except ValueError:
            originalRed, originalGreen, originalBlue = originalPixels[i]
        try:
            newRed, newGreen, newBlue, a = newPixels[i]
        except ValueError:
            newRed, newGreen, newBlue = newPixels[i]
        redDiff = newRed - originalRed
        blueDiff = newBlue - originalBlue
        greenDiff = newGreen - originalGreen
        diff.append([redDiff, greenDiff, blueDiff])

    rawDeStegaData = ""
    for r, g, b in diff:
        rawDeStegaData += str(r)
        rawDeStegaData += str(g)
        rawDeStegaData += str(b)

    # Trim 2s
    # offset = rawDeStegaData.find("5")
    # undecodedData = rawDeStegaData[offset:]
    undecodedData = rawDeStegaData.replace(str(BUFF_CHAR), "")
    for char in undecodedData:
        if char != '0' and char != '1':
            print char

    one_ring_to_bind_them = ''.join(undecodedData)
    bin_str = "0b" + one_ring_to_bind_them
    more_back = "%x" % int(bin_str, 2)
    bring_it_home = binascii.unhexlify(more_back)

    sys.stdout.write(
        "\t[+] Seems like that are %s bytes of information encoded in the file.\n" % len(bring_it_home))
    decompDat = zlib.decompress(bring_it_home)

    f = open(outputPath, 'wb')
    f.write(decompDat)
    f.close()
    sys.stdout.write(
        "\t[+] Decoding process complete and output written to %s.\n\n" % outputPath)


def PrepareBaseImage(imagePath, outputPath):
    sys.stdout.write("\nCreating New Base Image\n")
    sys.stdout.write("-" * len("Creating New Base Image") + "\n")
    img, ImageWidth, ImageHeight, TotalPixels = openImage(imagePath)
    pixels = image2pixelarray(img)

    FinalPixels = []
    for pixel in pixels:
        max_can_be = PIXEL_MAX-BUFF_CHAR
        if pixel[0] > max_can_be:
            red = max_can_be
        else:
            red = pixel[0]
        if pixel[1] > max_can_be:
            green = max_can_be
        else:
            green = pixel[0]
        if pixel[2] > max_can_be:
            blue = max_can_be
        else:
            blue = pixel[0]
        FinalPixels.append((red, green, blue))

    im2 = Image.new(img.mode, (ImageWidth, ImageHeight))
    im2.putdata(FinalPixels)
    im2.save(outputPath)
    sys.stdout.write("\t[+] New base image saved at '%s'.\n\n" % outputPath)


def _print_help():
    sys.stdout.write("\n\n")
    sys.stdout.write("Please choose one of the 3 modes:\n")
    for mode in MODES:
        sys.stdout.write("\t'%s'\n" % mode)
    sys.stdout.write("\n")
    sys.stdout.write("Base Image\n")
    sys.stdout.write("\tThis mode is to take an image and prepare it to being used for data exfiltration as base image.\n")
    sys.stdout.write("\tFor 'baseimage' you need to choose an original image as well as an output path.\n")
    sys.stdout.write("\tUse the following syntax: '%s baseimage originalImage.jpg outputpath.jpg'.\n\n" % sys.argv[0].split("/")[-1:][0])

    sys.stdout.write("Encode\n")
    sys.stdout.write("\tThis mode will encode a file into the new base image.\n")
    sys.stdout.write("\tYou need to specify base image, file to conceal and an output path.\n")
    sys.stdout.write("\tUse the following syntax: '%s encode baseImage.jpg /etc/passwd newImage.jpg'.\n\n" % sys.argv[0].split("/")[-1:][0])

    sys.stdout.write("Decode\n")
    sys.stdout.write("\tThis mode will decode a file into the data encoded within it.\n")
    sys.stdout.write("\tYou need to specify the file the information is concealed within, base image and an output path.\n")
    sys.stdout.write("\tUse the following syntax: '%s decode newImage.jpg baseImage passwdFile'.\n\n" % sys.argv[0].split("/")[-1:][0])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        _print_help()
        sys.exit()

    if sys.argv[1].strip() not in MODES:
        _print_help()
        sys.exit()

    if sys.argv[1].strip() == MODES[0]:
        # Base Image
        try:
            fname = sys.argv[2].strip()
            output = sys.argv[3].strip()
            PrepareBaseImage(imagePath=fname, outputPath=output)
        except IndexError:
            _print_help()
            sys.exit()

    elif sys.argv[1].strip() == MODES[1]:
        # Encode
        try:
            baseImage = sys.argv[2].strip()
            inputData = sys.argv[3].strip()
            outputPath = sys.argv[4].strip()
            CreateExfiltrationFile(originalImage=baseImage, rawData=inputData, OutputImage=outputPath)
        except IndexError:
            _print_help()
            sys.exit()

    elif sys.argv[1].strip() == MODES[2]:
        # Decode
        try:
            encodedImage = sys.argv[2].strip()
            baseImage = sys.argv[3].strip()
            outputPath = sys.argv[4].strip()
            DecodeExfiltrationFile(originalImage=baseImage, newImage=encodedImage, outputPath=outputPath)
        except IndexError:
            _print_help()
            sys.exit()
    else:
        _print_help()
        sys.exit()
