#!/usr/bin/python

import sys
import socket

WRITE_BINARY = "wb"
READ_FROM_SOCK = 7000
SKIP = 27

sys.stdout.write("Starting listener.\n")
try:
	# Open a raw socket listening on all IP addresses but only for ICMP
	sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
	sock.bind(('', 1))
	sys.stdout.write("Now listening...\n")
except:
	sys.stderr.write("Could not start listening.\nProbably not root.\n")
	sys.exit(-1)

files_received = 0
i = 0
try:
	while True:
		# receive data
		data = sock.recv(READ_FROM_SOCK)
		stri = ""

		# Get IP Header
		ip_header = data[:20]

		# Get IP
		ips = ip_header[-8:-4]
		source = "%i.%i.%i.%i" % (ord(ips[0]), ord(ips[1]), ord(ips[2]), ord(ips[3]))

		if (i == 0):
			sys.stdout.write("Connection from: %s\n" % source)
			size_offset = data.find(":")
			filename = data[27:size_offset]
			filename = filename.encode('ascii', 'replace')
			total_packets = data[size_offset + 1:]
			sys.stdout.write("Getting file: %s\n" % data[27:size_offset])
			sys.stdout.write("With %s packets.\n" % data[size_offset + 1:])
			fh = open(str(files_received), WRITE_BINARY)
			files_received = files_received + 1
			i += 1

		elif (data[27:35].find("\x00\x00\x00\x00") != -1):
			sys.stdout.write("Reached end of packet\n")
			sys.stdout.write("--------------------------------------\n")
			fh.close()
			i = 0
			continue

		else:
			# ToDo:
			# We really need to actually check for the terminator and not just send it ya'damb ass!
			sys.stdout.write(str(i) + "/" + str(total_packets) + "\n")
			data_end_offset = data.find("\x01\x02\x03\x04")
		fh.write(data[27:data_end_offset])
		i += 1

except KeyboardInterrupt:
	print ''