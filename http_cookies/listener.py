#!/usr/bin/python


# Code used for sniffer originally from http://www.binarytides.com/python-packet-sniffer-code-linux/

import sys
import zlib
import socket
import base64
from struct import *

# Constants
WRITE_BINARY = 'wb'

# Packet configuration
INIT_PACKET_COOKIE = "sessionID"
PACKET_COOKIE = "PHPSESSID"
TERMINATION_COOKIE = "sessID0"
COOKIE_DELIMITER = ".."
SLEEP = 0.05
COMPRESSION_LEVEL = 6


# Convert a string of 6 characters of ethernet address into a dash separated hex string
def eth_addr(a):
	b = "%.2x:%.2x:%.2x:%.2x:%.2x:%.2x" % (ord(a[0]), ord(a[1]), ord(a[2]), ord(a[3]), ord(a[4]), ord(a[5]))
	return b

#create a AF_PACKET type raw socket (thats basically packet level)
#define ETH_P_ALL    0x0003          /* Every packet (be careful!!!) */
try:
	s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
except socket.error, msg:
	print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	sys.exit()

# receive a packet
while True:
	packet = s.recvfrom(65565)

	#packet string from tuple
	packet = packet[0]

	#parse ethernet header
	eth_length = 14

	eth_header = packet[:eth_length]
	eth = unpack('!6s6sH', eth_header)
	eth_protocol = socket.ntohs(eth[2])

	# No use for this here, but keeping for legacy
	#'Destination MAC : ' + eth_addr(packet[0:6]) + ' Source MAC : ' + eth_addr(packet[6:12]) + ' Protocol : ' + str(eth_protocol)

	#Parse IP packets, IP Protocol number = 8
	if eth_protocol == 8:
		#Parse IP header
		#take first 20 characters for the ip header
		ip_header = packet[eth_length:20 + eth_length]

		#now unpack them :)
		iph = unpack('!BBHHHBBH4s4s', ip_header)

		version_ihl = iph[0]
		version = version_ihl >> 4
		ihl = version_ihl & 0xF

		iph_length = ihl * 4

		ttl = iph[5]
		protocol = iph[6]
		s_addr = socket.inet_ntoa(iph[8]);
		d_addr = socket.inet_ntoa(iph[9]);

		#print 'Version : ' + str(version) + ' IP Header Length : ' + str(ihl) + ' TTL : ' + str(ttl) + ' Protocol : ' + str(protocol) + ' Source Address : ' + str(s_addr) + ' Destination Address : ' + str(d_addr)

		#TCP protocol
		if protocol == 6:
			t = iph_length + eth_length
			tcp_header = packet[t:t + 20]

			#now unpack them :)
			tcph = unpack('!HHLLBBHHH', tcp_header)

			source_port = tcph[0]
			dest_port = tcph[1]
			sequence = tcph[2]
			acknowledgement = tcph[3]
			doff_reserved = tcph[4]
			tcph_length = doff_reserved >> 4

			#print 'Source Port : ' + str(source_port) + ' Dest Port : ' + str(dest_port) + ' Sequence Number : ' + str(sequence) + ' Acknowledgement : ' + str(acknowledgement) + ' TCP header length : ' + str(tcph_length)

			if (dest_port == 80) or (source_port == 80):
				filename = "dfbsdgbSFGBSbSRTBsrthbSFGNsrHS$5h"

				h_size = eth_length + iph_length + tcph_length * 4
				data_size = len(packet) - h_size

				#get data from the packet
				data = packet[h_size:]

				if data.find(INIT_PACKET_COOKIE) != -1:
					data_init_offset = data.find(INIT_PACKET_COOKIE)
					viable_data = data[data_init_offset:]  # Getting right line
					filename = viable_data[viable_data.find("\": \"") + 4:viable_data.find("..")]  # getting filename
					viable_data = viable_data[viable_data.find("..") + 2:]  # trim it
					crc = viable_data[:viable_data.find("..")]  # Getting CRC
					viable_data = viable_data[viable_data.find("..") + 2:]  # trim it
					total_packets = viable_data[:viable_data.find("\"}")]  # Getting packet amount

					sys.stdout.write("Got initiation packet from " + str(s_addr) + ".\n")
					sys.stdout.write("Will now initiate capturing of: \n")
					sys.stdout.write("\t\tFilename:\t%s\n" % filename)
					sys.stdout.write("\t\tCRC32:\t\t%s\n" % crc)
					sys.stdout.write("\t\tTotal Packets:\t%s\n" % total_packets)
					sys.stdout.write("\t\tOrigin IP:\t%s\n" % s_addr)

					data_packets_recvd = 0
					fh = open(filename + "_" + crc, WRITE_BINARY)
					recvd_data = ""

				# Found termination 
				elif data.find(TERMINATION_COOKIE) != -1:
					sys.stdout.write("TERM\n")
					if zlib.crc32(recvd_data) == int(crc):
						# CRC32 is matched. Continuing to decryption and file saving
						recvd_data = base64.b64decode(recvd_data)
						fh.write(recvd_data)
						fh.close()
						sys.stdout.write(
							"[+] File has been created and saved as " + str(filename) + "_" + str(crc) + "\n")
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
					pass

				#print data
				#print 'Data : ' + data

		# ICMP Packets: do nothing. Keeping to future use
		elif protocol == 1:
			pass

		# UDP packets: do nothing. Keeping to future use
		elif protocol == 17:
			pass

		# Other types. Keep for legacy
		else:
			pass

			#print