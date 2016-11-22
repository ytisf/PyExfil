#!/usr/bin/python

import os
import sys
import zlib
import time
import datetime
import base64
from socket import *
from impacket import ImpactPacket


""" Constants """
READ_BINARY = "rb"
WRITE_BINARY = "wb"
READ_FROM_SOCK = 7000
ICMP_HEADER_SIZE = 27
DATA_SEPARATOR = "::"
DATA_TERMINATOR = "\x12\x13\x14\x15"
INIT_PACKET = "\x12\x11\x13\x12\x12\x12"
END_PACKET = "\x15\x14\x13\x12"
LOGFILE_BASENAME = "icmp_log"
LOGFILE_EXT = ".txt"


def send_file(ip_addr, src_ip_addr="127.0.0.1", file_path="", max_packetsize=512, SLEEP=0.1):
	"""
	send_file will send a file to the ip_addr given.
	A file path is required to send the file.
	Max packet size can be determined automatically.
	:param ip_addr: IP Address to send the file to.
	:param src_ip_addr: IP Address to spoof from. Default it 127.0.0.1.
	:param file_path: Path of the file to send.
	:param max_packetsize: Max packet size. Default is 512.
	:return:
	"""

	if file_path == "":
		sys.stderr.write("No file path given.\n")
		return -1

	# Load file
	fh = open(file_path, READ_BINARY)
	iAmFile = fh.read()
	fh.close()

	# Create Raw Socket
	s = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
	s.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)

	# Create IP Packet
	ip = ImpactPacket.IP()
	ip.set_ip_src(src_ip_addr)
	ip.set_ip_dst(ip_addr)

	# ICMP on top of IP
	icmp = ImpactPacket.ICMP()
	icmp.set_icmp_type(icmp.ICMP_ECHOREPLY)

	# Fragmentation of DATA
	x = len(iAmFile) / max_packetsize
	y = len(iAmFile) % max_packetsize

	seq_id = 0

	# Calculate File:
	IamDone = base64.b64encode(iAmFile)  # Base64 Encode for ASCII
	checksum = zlib.crc32(IamDone)  # Build CRC for the file

	# Get file name from file path:
	head, tail = os.path.split(file_path)

	# Build stream initiation packet
	current_packet = ""
	current_packet += tail + DATA_SEPARATOR + str(checksum) + DATA_SEPARATOR + str(x + 2) + DATA_TERMINATOR + INIT_PACKET
	icmp.contains(ImpactPacket.Data(current_packet))
	ip.contains(icmp)
	icmp.set_icmp_id(seq_id)
	icmp.set_icmp_cksum(0)
	icmp.auto_checksum = 1
	s.sendto(ip.get_packet(), (ip_addr, 0))
	time.sleep(SLEEP)
	seq_id += 1

	# Iterate over the file
	for i in range(1, x + 2):
		str_send = IamDone[max_packetsize * (i - 1): max_packetsize * i] + DATA_TERMINATOR
		icmp.contains(ImpactPacket.Data(str_send))
		ip.contains(icmp)
		icmp.set_icmp_id(seq_id)
		icmp.set_icmp_cksum(0)
		icmp.auto_checksum = 1
		s.sendto(ip.get_packet(), (ip_addr, 0))
		time.sleep(SLEEP)
		seq_id += 1

	# Add last section
	str_send = IamDone[max_packetsize * i:max_packetsize * i + y] + DATA_TERMINATOR
	icmp.contains(ImpactPacket.Data(str_send))
	ip.contains(icmp)
	seq_id += 1
	icmp.set_icmp_id(seq_id)
	icmp.set_icmp_cksum(0)
	icmp.auto_checksum = 1
	s.sendto(ip.get_packet(), (ip_addr, 0))
	time.sleep(SLEEP)

	# Send termination package
	str_send = (tail + DATA_SEPARATOR + checksum + DATA_SEPARATOR + seq_id + DATA_TERMINATOR + END_PACKET)
	icmp.contains(ImpactPacket.Data(str_send))
	ip.contains(icmp)
	seq_id += 1
	icmp.set_icmp_id(seq_id)
	icmp.set_icmp_cksum(0)
	icmp.auto_checksum = 1
	s.sendto(ip.get_packet(), (ip_addr, 0))

	return 0


def init_listener(ip_addr, saving_location="."):
	"""
	init_listener will start a listener for incoming ICMP packets
	on a specified ip_addr to receive the packets. It will then
	save a log file and the incoming information to the given path.

	If none given it will generate one itself.
	:param ip_addr: The local IP address to bind the listener to.
	:return: Nothing.
	"""

	# Trying to open raw ICMP socket.
	# If fails, you're probably just not root
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
		sock.bind(('', 1))
		sys.stdout.write("Now listening...\n")
	except:
		sys.stderr.write("Could not start listening.\nProbably not root.\n")
		raise ()

	# Resetting counters
	files_received = 0
	i = 0
	current_file = ""

	# init log file:
	current_time_as_string = str(datetime.datetime.now()).replace(":",".").replace(" ", "-")[:-7]
	log_fh = open(LOGFILE_BASENAME + current_time_as_string + LOGFILE_EXT, WRITE_BINARY)
	log_fh.write("Started logging at %s\n\n" % current_time_as_string)

	while True:
		# Extract data from IP header
		data = sock.recv(READ_FROM_SOCK)                # Get data
		ip_header = data[:20]                           # Extract IP Header
		# Get IP
		ips = ip_header[-8:-4]
		source = "%i.%i.%i.%i" % (ord(ips[0]), ord(ips[1]), ord(ips[2]), ord(ips[3]))

		if data[27:].find(INIT_PACKET) != -1:
			# Extract data from Initiation packet:
			man_string = data[27:]                              # String to manipulate
			man_array = man_string.split(DATA_SEPARATOR)        # Exploit data into array
			filename = man_array[0]
			checksum = man_array[1]
			amount_of_packets = man_array[2]

			# Document to log file
			log_fh.write("Received file:\n")
			log_fh.write("\tFile name:\t%s\n" % filename)
			log_fh.write("\tIncoming from:\t%s\n" & source)
			log_fh.write("\tFile checksum:\t%s\n" % checksum)
			log_fh.write("\tIn Packets:\t%s\n" % amount_of_packets)
			log_fh.write("\tIncoming at:\t%s\n" % str(datetime.datetime.now()).replace(":", ".").replace(" ", "-")[:-7])

		elif data[27:].find(END_PACKET) != -1:
			# Extract data from Initiation packet:
			man_string = data[27:]                              # String to manipulate
			man_array = man_string.split(DATA_SEPARATOR)        # Exploit data into array
			if filename != man_array[0]:
				sys.stderr.write("You tried transferring 2 files simultaneous. Killing my self now!\n")
				log_fh.write("Detected 2 file simultaneous. Killing my self.\n")
				return -1

			else:
				log_fh.write("Got termination packet for %s\n" % man_array[0])
				comp_crc = zlib.crc32(current_file)
				if str(comp_crc) == checksum:
					# CRC validated
					log_fh.write("CRC validation is green for " + str(comp_crc) + " with file name: " + filename + "\n")
					current_file = base64.b64decode(current_file)

					# Write to file
					fh = open(filename + "_" + checksum, WRITE_BINARY)
					fh.write(current_file)
					fh.close()
					files_received += 1

				else:
					# CRC failed
					log_fh.write("CRC validation FAILED for '" + str(comp_crc) + "' with : " + checksum + "\n")

			# Resetting counters:
			i = 0
			filename = ""
			data = ""
			man_string = ""
			man_array = []

		elif data[27:].find(DATA_SEPARATOR) != -1:
			# Found a regular packet
			current_file += data[27:data.find(DATA_TERMINATOR)]
			log_fh.write("Received packet %s" % i)
			i += 1


if __name__ == "__main__":
	sys.stdout.write("This is meant to be a module for python and not a stand alone executable\n")