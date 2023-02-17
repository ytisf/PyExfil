#!/usr/bin/env python3

try:
	import cv2
except ImportError:
	print("OpenCV library not found. Please install OpenCV to use this script with pip install opencv-python.")
	exit(1)
import hashlib
import os
import sys

try:
	from PIL import Image
except ImportError:
	print("PIL library not found. Please install PIL to use this script with pip install pillow.")
	exit(1)


try:
	# import pylibdmtx
	from pylibdmtx.pylibdmtx import decode, encode
except ImportError as e:
	if "Unable to find dmtx" in str(e):
		print("libdmtx not found. Please install it with:")
		print("\tOn MacOS: brew install libdmtx")
		print("\tOn Ubuntu: sudo apt-get install libdmtx-dev")
		exit(1)
	else:
		print("pylibdmtx not found. Please install it with pip install pylibdmtx.")
		exit(1)

import numpy as np


KEY      = b'\x29\x12\x88\x16\x05\x16\x31\x05\x19\x05\x02\x21'



class DataMatrixOverLSB():
	def __init__(self, verbose=True, debug=True):
		self._VERBOSE   = verbose
		self.DEBUG      = debug
		self.SUCCESS    = 'success'
		self.ERROR      = 'error'
		self.INFO       = 'info'
	
	def _print(self, message, level='info') -> None:
		message = message.strip()
		if level == self.INFO:
			# print with blue [-] prefix:
			sys.stdout.write(f'\033[94m[-]\033[0m {message}\n')
		elif level == self.ERROR:
			# print with red [!] prefix:
			sys.stdout.write(f'\033[91m[!]\033[0m {message}\n')
		elif level == self.SUCCESS:
			# print with green [+] prefix:
			sys.stdout.write(f'\033[92m[+]\033[0m {message}\n')
		else:
			raise ValueError('level must be one of info, error, success')

	def clear_bit(self, value, bit_index=0):
		if bit_index < 8:
			return value & ~(1 << bit_index)
		else:
			return value
	
	def get_bit(self, value, bit_index=0):
		if bit_index < 8:
			return value & (1 << bit_index)
		else:
			return 0

	def set_bit(self, value, bit_index=0):
		if bit_index < 8:
			return value | (1 << bit_index)
		else:
			return value

	def _xor_bytes(self, a: bytes, b: bytes) -> bytes:
		return bytes(x ^ y for x, y in zip(a, b))

	def _read_image_into_rgb_array(self, image_path: str) -> list:
		'''
		Reads an image into an RGB array
		args:
			image_path: path to image
		returns:
			list of RGB values
		'''
		img = cv2.imread(image_path)
		return img.reshape((img.shape[0] * img.shape[1], 3)), img.shape[0], img.shape[1]

	def _create_datamatrix_file(self, data: bytes, filename: str) -> str:
		encoded = encode(data)
		img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
		img.save(filename)
		return filename

	def _zero_lsb(self, pixels: list) -> list:
		empty = []
		for r,g,b in pixels:
			empty.append([self.clear_bit(r), self.clear_bit(g), self.clear_bit(b)],)
		return empty

	def _save_pixels_to_image(self, pixels: list, size: tuple, filename: str) -> str:
		final_packet_pixels = np.array(pixels, dtype=np.uint8)
		final_packet_pixels = final_packet_pixels.reshape(size)
		cv2.imwrite(filename, final_packet_pixels)
		return filename

	def _pull_down_pixels(self, pixels: list) -> list:
		output = []
		for i, _ in enumerate(pixels):
			r,g,b = pixels[i]
			nr,ng,nb = r,g,b
			# if r is bigger than 100 set nr = 1 bit:
			if r > 100:
				nr = 1
			else:
				nr = 0
			if b > 100:
				nb = 1
			else:
				nb = 0
			if g > 100:
				ng = 1
			else:
				ng = 0
			output.append([nr,ng,nb])
		return output

	def _merge_arrays(self, pixels_original, pylled_arr):
		for i, px in enumerate(pylled_arr):
			# if bit of pylled_arr is 1, set LSB of pixels_original to 1:
			if px[0] == 1:
				pixels_original[i][0] = self.set_bit(pixels_original[i][0])
			if px[1] == 1:
				pixels_original[i][1] = self.set_bit(pixels_original[i][1])
			if px[2] == 1:
				pixels_original[i][2] = self.set_bit(pixels_original[i][2])
		return pixels_original

	def _get_only_last_bit(self, pixel_array):
		# create empty array the size and shape of the input array:
		output = np.zeros(pixel_array.shape, dtype=np.uint8)

		for i in range(pixel_array.shape[0]):
			for j in range(3):
				# get last bit of each pixel:
				if self.get_bit(pixel_array[i][j]) == 1:
					output[i][j] = 255
				else:
					output[i][j] = 0
		return output

	def Encode(self, data: bytes, mapping_file_path: str, output_file_path: str) -> str:
		pixels_array_original,h,w = self._read_image_into_rgb_array(mapping_file_path)
		dm_file_path = self._create_datamatrix_file(data, f'_1_datamatrix.png')

		# read the image into pixels array:
		pixels_array_dm = self._read_image_into_rgb_array(dm_file_path)
		# os.remove(dm_file_path)
		if self._VERBOSE:
			self._print(f'Data was converted into DataMatrix and stored in memory.', level=self.SUCCESS)
		
		# zero the LSB of the pixels:
		zeroed_pixels_array_original = self._zero_lsb(pixels_array_original)
		self._save_pixels_to_image(zeroed_pixels_array_original,(h,w,3) ,'_2_zeroed.png')
		if self._VERBOSE:
			self._print(f'LSB of the pixels was zeroed.', level=self.INFO)
		
		# # convert data matrix pixels to pull up or down:
		pixels_array_dm = self._pull_down_pixels(self._read_image_into_rgb_array(dm_file_path)[0])
		if self._VERBOSE:
			self._print(f'DataMatrix pixels were converted to pull up or down.', level=self.INFO)

		# # merge the two arrays:
		pixels_array_original = self._merge_arrays(zeroed_pixels_array_original, pixels_array_dm)
		if self._VERBOSE:
			self._print(f'DataMatrix pixels were merged with the original image map.', level=self.INFO)

		self._save_pixels_to_image(pixels_array_original,(h,w,3) , output_file_path)
		if self._VERBOSE:
			self._print(f'DataMatrix pixels were merged with the original image map.', level=self.SUCCESS)

		return output_file_path

	def Decode(self, image_path: str) -> str:
		encoded_pixels, w, h = self._read_image_into_rgb_array(image_path)
		if self._VERBOSE:
			self._print(f'Image was read into memory.', level=self.SUCCESS)

		# turn encoded_pixels into a numpy array:
		output_array = np.array(encoded_pixels, dtype=np.uint8)

		# read only last bit from each pixel
		output_array = self._get_only_last_bit(pixel_array=output_array)
		if self._VERBOSE:
			self._print(f'Last bit of each pixel was read.', level=self.INFO)

		# convert output_array to a 1D array of '0' and '1' characters
		string_output_array = ''.join(str(e) for e in output_array.flatten())

		# pad the string with zeros so that its length is a multiple of 8
		remainder = len(string_output_array) % 8
		if remainder != 0:
			string_output_array += '0' * (8 - remainder)

		# split the string into 8-bit groups and convert to integers
		output_list = [int(string_output_array[i:i+8], 2) for i in range(0, len(string_output_array), 8)]

		# reshape for the output:
		output_array = np.array(output_list, dtype=np.uint8).reshape((h, w, 3))

		# save to image file:
		self._save_pixels_to_image(output_array,(w,h, 3), '_decoded_.png')


if __name__ == "__main__":
    sys.stderr.write("This is not a standalone script. Please import it as a module.\n")
    sys.exit(1)