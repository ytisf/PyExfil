# coding=utf-8

import os
import sys
import zlib
import binascii


from pyexfil.includes.prepare import _splitString


# ASCII
asciicodes = [' ','!','"','#','$','%','&','','(',')','*','+',',','-','.','/',
		  '0','1','2','3','4','5','6','7','8','9',':',';','<','=','>','?','@',
		  'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q',
		  'r','s','t','u','v','w','x','y','z','[','\\',']','^','_']

# Braille symbols
brailles = ['⠀','⠮','⠐','⠼','⠫','⠩','⠯','⠄','⠷','⠾','⠡','⠬','⠠','⠤','⠨','⠌','⠴','⠂','⠆','⠒','⠲','⠢',
		'⠖','⠶','⠦','⠔','⠱','⠰','⠣','⠿','⠜','⠹','⠈','⠁','⠃','⠉','⠙','⠑','⠋','⠛','⠓','⠊','⠚','⠅',
		'⠇','⠍','⠝','⠕','⠏','⠟','⠗','⠎','⠞','⠥','⠧','⠺','⠭','⠽','⠵','⠪','⠳','⠻','⠘','⠸']

# Mapping Lists
N_BRAILLES      = []
N_ASCIICODES    = []


def _prep_brailles_system():
	global N_BRAILLES
	global N_ASCIICODES

	# Since in Brailles' A-F are same signs as 1-6 we will convert
	# the A-F to G-L.
	num_s = asciicodes.index("0")
	for i in range(num_s, num_s+10):
		N_BRAILLES.append(brailles[i])
		N_ASCIICODES.append(asciicodes[i])
	num_s = asciicodes.index("g")
	for i in range(num_s, num_s+6):
		N_BRAILLES.append(brailles[i])
		N_ASCIICODES.append(asciicodes[i])

	return True


def _create_image(text):
	dubb = _splitString(text, 90)
	o_file = open("output.txt", 'wb')
	for i in dubb:
		o_file.write(bytes(i, 'utf-8'))
		o_file.write(bytes("\n", 'utf-8'))
	o_file.close()
	os.system("python pyexfil/Stega/braille/txt2pdf/txt2pdf.py -q -s 8 -o output.pdf -f \"Apple Braille.ttf\" output.txt")


def read_and_prep_file(file_path):
	data = zlib.compress(open(file_path, 'rb').read(), level=9)
	temp = str(binascii.hexlify(data))[2:-1]
	for i in range(97,97+6):
		temp = temp.replace(chr(i), chr(i+6))

	output = []
	for rr in temp:
		output.append(N_BRAILLES[N_ASCIICODES.index(rr.lower())])
	return ''.join(output)


def decode_data(data):
	if N_BRAILLES == [] or N_ASCIICODES == []:
		_prep_brailles_system()
	output = []
	try:
		for rr in data:
			output.append(N_ASCIICODES[N_BRAILLES.index(rr)])
	except:
		sys.stderr.write("Data is not properly encoded.\n")
		return None
	output = ''.join(output)
	for i in range(97+6,97+12):
		output = output.replace(chr(i), chr(i-6))
	output = binascii.unhexlify(output)
	try:
		return zlib.decompress(output)
	except:
		sys.stderr.write("Data was not zlib compressed.\n")
		return None


# Start up
_prep_brailles_system()


def Send(file_path='/etc/passwd', to_screen=False, to_file=False):
	encoded_file = read_and_prep_file(file_path)
	if to_screen:
		sys.stdout.write(encoded_file)
	if to_file:
		_create_image(encoded_file)


def Decode(data):
	res = decode_data(data)
	if res is not None:
		print(res)
	