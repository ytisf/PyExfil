import string
import struct


def inet_aton (packme):
	"""Given a IP address as a string of the form 123.45.67.89, pack
	   it into the 32-bit binary representation (struct in_addr) used
	   in C and other languages."""
	try:
		a, b, c, d = map(string.atoi, string.split(packme, '.'))
		return struct.pack('BBBB', a, b, c, d)
	except:
		return False
	
	
def inet_ntoa (packed):
	"""Unpacks a 32-bit binary representation of an IP address into a
	   string and return it in dotted-quad (123.45.67.89) format."""
	try:
		quads = map(str, struct.unpack('BBBB', packed))
		return string.join(quads, '.')
	except:
		return False