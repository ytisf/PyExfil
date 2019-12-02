
import os
import sys
import array

from PIL import Image

from pyexfil.includes.general import _is_slice_in_list
from pyexfil.includes.encryption_wrappers import AESEncryptOFB, AESDecryptOFB
from pyexfil.includes.image_manipulation import _openImage, _image2pixelarray


MAX_IMAGE_ROW_LENGTH        = 1024
TERMINATOR                  = [46, 37, 46, 49, 39, 31, 92, 55, 92, 77, 67,
                               11, 39, 98, 48, 82, 40, 12, 85, 83, 61, 60,
                               35, 63, 70, 76, 60, 10, 47, 10, 18, 19, 42,
                               95, 55, 96, 19, 89, 46, 76, 78, 37, 44, 94,
                               48, 25, 53]
TEST_PNG                    = 'pyexfil/Stega/png_transparency/PyExfil_Logo.png'
TEST_OUTPUT_PATH            = 'output.png'


class Encode(object):
	
	def __init__(self, key, data, png_file=TEST_PNG, output_path=TEST_OUTPUT_PATH, verbose=False):
		if type(data) is not str:
			raise("data parameter must be 'str' type.")
		if png_file is None:
			sys.stdout.write("Will generate an empty picture. You can also specify a path to an existing PNG/JPEG file.\n")
			self.generate_empty_image = True
		else:
			self.generate_empty_image = False
			self.png_path = png_file
			
		self.key                    = key
		self.data                   = data
		self.output_name            = output_path
		self.verbose                = verbose
		self.encrypted_data         = None
		self.encrypted_array        = []
		self.line_count             = 1
		
		self.initialize()
		
	def initialize(self):
		if not self.generate_empty_image:
			if os.path.isfile(self.png_path):
				pass
			else:
				if self.verbose: sys.stderr.write("File path to '%s' was not found.\nWill continue with empty image.\n" % self.png_path)
				self.generate_empty_image = True
		
		try:
			self.encrypted_data = AESEncryptOFB(key=self.key, text=self.data)
			self.encrypted_array = array.array('B', self.encrypted_data)
		except Exception as e:
			if self.verbose: sys.stderr.write("Error encrypting data with '%s'.\n" % str(e))
			raise e
		
		self.line_count = int(len(self.encrypted_array)/MAX_IMAGE_ROW_LENGTH) + 1
		
	def Run(self):
		finalArray = []
		if not self.generate_empty_image:
			imgObj = _openImage(self.png_path)
			pxlsArray = _image2pixelarray(imgObj[0])
		else:
			pxlsArray = []
			for line in range(0, len(self.encrypted_data) + 1 + len(TERMINATOR)):
				pxlsArray.append([255, 255, 255, 0])
		
		# Add encrypted data
		for index in range(0, len(self.encrypted_array)):
			finalArray.append(  (pxlsArray[index][0],
			                     pxlsArray[index][1],
			                     pxlsArray[index][2],
			                     self.encrypted_array[index]))
		
		# Add terminator
		i = 0
		for index in range(len(self.encrypted_array), len(self.encrypted_array) + len(TERMINATOR)):
			finalArray.append(
					(pxlsArray[index][0], pxlsArray[index][1], pxlsArray[index][2], TERMINATOR[i])
			)
			i += 1
			
		if len(self.encrypted_array) + len(TERMINATOR) < len(pxlsArray):
			starting_point = len(self.encrypted_array) + len(TERMINATOR)
			diff = len(pxlsArray) - starting_point
			finalArray.extend(pxlsArray[starting_point:])
		
		if imgObj[1] * imgObj[2] < len(finalArray):
			if self.verbose:
				sys.stderr.write("Image size is too small for the size of the data.\n")
			raise("Image too small for data.")
		
		else:
			bg = Image.open(self.png_path, 'r')
			text_img = Image.new('RGBA', (imgObj[1], imgObj[2]), (0, 0, 0, 0))
			text_img.putdata((finalArray))
			text_img.save(self.output_name, format="png")
			if self.verbose:
				sys.stdout.write("New image saved to '%s'.\n" % self.output_name)
		return True


class Decode():
	def __init__(self, key, file_path, verbose=False):
		self.key            = key
		self.file_path      = file_path
		self.verbose        = verbose
		
	def Run(self):
		if not os.path.isfile(self.file_path):
			if self.verbose:
				sys.stderr.write("File '%s' was not found.\n" % self.file_path)
			return False
		
		try:
			imgObj = _openImage(self.file_path)
			pxlsArray = _image2pixelarray(imgObj[0])
		except Exception as e:
			if self.verbose: sys.stderr.write("Error reading file '%s'.\n%s\n" % (self.file_path, str(e)) )
			return False
		
		search_array = []
		for pixel in pxlsArray:
			search_array.append(pixel[3])
		
		if _is_slice_in_list(s=TERMINATOR, l=search_array):
			if self.verbose: sys.stdout.write("Found terminator in file. It seems like data is there.\n")
		else:
			if self.verbose: sys.stderr.write("Could not find terminator in the file. Is it encoded?\n")
			return False
		
		terminator_as_binary = bytes(array.array('B', TERMINATOR))
		encrypted_data_as_binary = bytes(array.array('B', search_array))
		encrypted_data_as_binary = encrypted_data_as_binary[:encrypted_data_as_binary.find(terminator_as_binary)]
		
		try:
			dec_data = AESDecryptOFB(key=self.key, text=encrypted_data_as_binary)
		except Exception as e:
			if self.verbose: sys.stderr.write("Could not decrypt data.\n%s.\n" % (str(e)))
			return False
		
		if self.verbose: sys.stdout.write("Data decrypted.\n")
		return dec_data

