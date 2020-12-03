from PIL import Image


def _openImage(image_path):
    """
    Opens image path as PIL Image Object
    :param image_path: String, image path
    :return: imgObj, ImageWidth, ImageHeight, TotalPixels
    """
    imgObj = Image.open(image_path)
    ImageWidth, ImageHeight = imgObj.size
    TotalPixels = ImageWidth * ImageHeight
    return imgObj, ImageWidth, ImageHeight, TotalPixels


def _image2pixelarray(imgObj):
    """
    Return image object as a pixel array list.
    :param imgObj: PIL Image Object
    :return: List, pixels
    """
    pixels = list(imgObj.getdata())
    return pixels
