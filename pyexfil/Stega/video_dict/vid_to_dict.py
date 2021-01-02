#!/usr/bin/python

"""
Install cv2 on OSX
brew tap homebrew/science
brew install opencv
export PYTHONPATH=/usr/local/lib/python2.7/site-packages:$PYTHONPATH
"""

# GLOBALS
FRAMES_FOLDER = "lala"
MAX_FRAMES = 10


import os
import sys
import cv2
import zlib
import random

try:
    import numpy as np
    from PIL import Image
    from pytube import YouTube
except ImportError, e:
    sys.stderr.write("Please install the dependencies needed.\n")
    sys.stderr.write("\t%s\n" % e)
    sys.exit(1)


BYTES = range(0, 256)
INDEX_MAP = {}


def _getYouTubeVideo(url):
    try:
        yt = YouTube(url)
        sys.stdout.write("[.]\tGetting video.\n")
        video = yt.get('mp4', '720p')
        video.download('/tmp/main.mp4', filename='Current')
        sys.stdout.write("[.]\tVideo saved to /tmp/main.mp4.\n")
        return True
    except:
        return False

def _map_images_to_bytes(folder_path, all_frames):
    global INDEX_MAP
    bytes_to_map = BYTES

    for fpath in all_frames:
        img, ImageWidth, ImageHeight, TotalPixels = openImage(folder_path+"/"+fpath)
        frame_index = int(fpath.replace("frame_", "").replace(".jpg", ""))
        pixels = image2pixelarray(img)
        for i in range(0, len(pixels)):
            r,g,b = pixels[i][0], pixels[i][1], pixels[i][2]
            if len(bytes_to_map) == 0:
                return True
                sys.stdout.write("[+]\tDone mapping!\n")
            for byte_left in bytes_to_map:
                if byte_left == r:
                    INDEX_MAP[byte_left] = {"frame": frame_index,"pixel": i,"colour": "r"}
                    bytes_to_map.remove(byte_left)
                elif  byte_left == g:
                    INDEX_MAP[byte_left] = {"frame": frame_index,"pixel": i,"colour": "g"}
                    bytes_to_map.remove(byte_left)
                elif  byte_left == b:
                    INDEX_MAP[byte_left] = {"frame": frame_index,"pixel": i,"colour": "b"}
                    bytes_to_map.remove(byte_left)
    return False

def _openFile(fpath):
    try:
        f = open(fpath, 'rb')
        data = f.read()
        f.close()
        return data
    except IOError, e:
        sys.stdout.write("[-]\tGot an error opening the file '%s'.\n" % fpath)
        sys.stdout.write("[-]\t%s.\n" % e)
        return False

def openImage(image_path):
    # Open Image
    try:
        img = Image.open(image_path)
        ImageWidth, ImageHeight = img.size
        TotalPixels = ImageWidth * ImageHeight
        return img, ImageWidth, ImageHeight, TotalPixels
    except IOError, e:
        sys.stderr.write("[!]\tError opening file '%s'.\n" % image_path)
        return False

def image2pixelarray(imgObj):
    arr = np.array(imgObj)
    pixels = list(imgObj.getdata())
    return pixels

def _create_tmp_dir():
    try:
        os.mkdir(FRAMES_FOLDER)
        return True
    except:
        return False

def DecodeDictionary(originalVideo, dictionaryFile, outputFile):
    sys.stdout.write("\n")
    _create_tmp_dir()       # Create temporary file

    # Break down dic
    dictionary = {}
    lines = _openFile(dictionaryFile).split(";")
    for i in range(0, len(lines)):
        try:
            dictionary[i] = {   "colour": lines[i].split(",")[0],
                                "frame": int(lines[i].split(",")[1]),
                                "pixel": int(lines[i].split(",")[2])
                            }
        except:
            # Probably empty line
            pass

    # Get all frames needed:
    frames = []
    for i in range(0, len(dictionary)):
        if dictionary[i]['frame'] in frames:
            continue
        else:
            frames.append(dictionary[i]['frame'])
    sys.stdout.write("[.]\tWe need to extract a total of %s frames.\n" % len(frames))

    # Try to get the video file
    try:
        vidcap = cv2.VideoCapture(originalVideo)
        success, image = vidcap.read()
        sys.stdout.write("[.]\tWas able to load video file '%s'.\n" % originalVideo)
    except:
        sys.stderr.write("[!]\tSeems like the file is not a valid video file.\n")
        sys.exit(1)

    # Read and save the frames we need
    for i in range(0,50):
        success,image = vidcap.read()
        if i > frames[-1:][0]:
            sys.stdout.write("[+]\tGot all the frames i need.\n")
            break
        if i in frames:
            sys.stdout.write("[.]\tGot to frame %s which i need.\n" % i)
            cv2.imwrite("%s/_frame_%d.jpg" % (FRAMES_FOLDER, i), image)     # save frame as JPEG file
            i += 1
        else:
            i += 1

    # Open all the images for quick searching but hogging RAM.
    # Fuck it, i'm Python!
    frames_pixels = {}
    for frame in frames:
        img, ImageWidth, ImageHeight, TotalPixels = openImage("%s/_frame_%d.jpg" % (FRAMES_FOLDER, frame))
        pixels = image2pixelarray(img)
        frames_pixels[frame] = pixels

    # Start decoding:
    DecodedData = ""
    for i in range(0, len(dictionary)):
        if dictionary[i]['colour'] == 'r':
            offset = 0
        elif dictionary[i]['colour'] == 'g':
            offset = 1
        elif dictionary[i]['colour'] == 'b':
            offset = 2

        DecodedData += chr(frames_pixels[dictionary[i]['frame']][dictionary[i]['pixel']][offset])

    # Decode:
    sys.stdout.write("[.]\tLength of decoded data is %s.\n" % len(DecodedData))
    unzip = zlib.decompress(DecodedData)
    sys.stdout.write("[.]\tLength of decoded unzipped data is %s.\n" % len(unzip))
    f = open(outputFile, 'wb')
    f.write(unzip)
    f.close()
    sys.stdout.write("[+]\tFile has been decoded and saved to '%s'.\n" % outputFile)
    sys.stdout.write("\n")

def TranscriptData(video_file, input_file, output_index):

    sys.stdout.write("\n")
    _create_tmp_dir()
    if not os.path.isfile(video_file):
        sys.stderr.write("[!]\tCould not find file '%s'.\n" % video_file)
        sys.exit(1)

    try:
        vidcap = cv2.VideoCapture(video_file)
        success,image = vidcap.read()
    except:
        sys.stderr.write("[!]\tSeems like the file is not a valid video file.\n")
        sys.exit(1)

    sys.stdout.write("[+]\tFinished reading the movie file.\n")
    sys.stdout.write("[+]\tStarting to process frames.\n\t(Generating Frames...) ")
    count = 0
    image_index = 0
    success = True
    all_frames = []
    while success:
        # Test if max frames had been reached
        if count == MAX_FRAMES:
            sys.stdout.write("\n")
            sys.stdout.write("[+]\tGot to %s frames and i wont need more.\n" % MAX_FRAMES)
            break

        # Do about 2 out of 3
        test_me = random.randint(11111,99999)
        if test_me % 3 == 0:
            success,image = vidcap.read()
            sys.stdout.write(".")
            sys.stdout.flush()
            cv2.imwrite("%s/frame_%d.jpg" % (FRAMES_FOLDER, image_index), image)     # save frame as JPEG file
            all_frames.append('frame_%d.jpg' % image_index)
            count += 1
            image_index += 1
        else:
            success,image = vidcap.read()
            sys.stdout.write("*")
            sys.stdout.flush()
            image_index += 1
            continue

    # Get the frames and map bytes to matching r,g,b values.
    bytes_map = _map_images_to_bytes(FRAMES_FOLDER, all_frames)
    if bytes_map is False:
        sys.stderr.write("[!]\tSeems like the video does not have variating pixels!\n")
        raise
    else:
        sys.stdout.write("[+]\tCreated an index for all binary values in the frames.\n")

    # Get and compress the data
    data_to_exfil = _openFile(input_file)
    compressed_data = zlib.compress(data_to_exfil, 9)
    sys.stdout.write("[.]\tGoing to create a dictionary for %s bytes of compressed data.\n" % len(compressed_data))

    # Map it out to plots
    encoded = []
    for byte in compressed_data:
        encoded.append(INDEX_MAP[ord(byte)])

    # Generate Short_String from that data:
    string_it = ""
    for data in encoded:
        string_it += data['colour'] +","+str(data['frame']) +","+str(data['pixel'])+";"

    f = open(output_index, 'w')
    f.write(string_it)
    f.close()

    zipped_dictionary = zlib.compress(string_it)
    f = open(output_index+".zip", 'wb')
    f.write(zipped_dictionary)
    f.close()

    sys.stdout.write("[+]\tOutput dictionary has been save to %s.\n" % output_index)
    sys.stdout.write("[+]\tAlso a zipped dictionary has been save to %s.\n" % (output_index+".zip"))
    sys.stdout.write("\n")

if __name__ == "__main__":
    TranscriptData(video_file=MOVIE_NAME, input_file="/etc/passwd", output_index="output.map")
    DecodeDictionary(originalVideo=MOVIE_NAME, dictionaryFile='output.map', outputFile="r")
