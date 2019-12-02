import struct
try:
	import string
except ImportError as e:
	pass

def _is_slice_in_list(s, l):
	"""
	Check if list s in in list l
	:param s: first array
	:param l: second array
	:return: bool
	"""
	len_s = len(s)
	return any(s == l[i:len_s + i] for i in range(len(l) - len_s + 1))


def _split_every_n (string, n):
	return [string[i:i + n] for i in range(0, len(string), n)]


def _icmp_checksum(data):
	"""
	Generate ICMP checksum
	:param data: str/bytes
	:return: checksum
	"""
	s = 0
	n = len(data) % 2
	for i in range(0, len(data) - n, 2):
		s += (ord(data[i]) << 8) + (ord(data[i + 1]))
	if n: s += (ord(data[i + 1]) << 8)
	while s >> 16: s = (s & 0xFFFF) + (s >> 16)
	s = ~s & 0xFFFF
	return s


def inet_aton (packed):
	"""Given a IP address as a string of the form 123.45.67.89, pack
	   it into the 32-bit binary representation (struct in_addr) used
	   in C and other languages."""
	try:
		quads = map(str, struct.unpack('BBBB', packed))
		return string.join(quads, '.')
	except:
		return False
