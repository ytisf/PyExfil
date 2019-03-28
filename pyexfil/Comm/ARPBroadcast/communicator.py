#!/usr/bin/env python2.7

import logging
import thread

from scapy.all import *
from scapy.all import Ether, ARP, Raw, sniff, sendp, Padding

import sys
sys.path.append("../../../")
from pyexfil.includes.encryption_wrappers import AESDecryptOFB, AESEncryptOFB
from pyexfil.includes.encryption_wrappers import PYEXFIL_DEFAULT_PASSWORD

# compatibility
try:
	input = raw_input
except NameError:
	pass

logging.getLogger().setLevel(logging.DEBUG)


def testCallBack(originalFrame, decryptedMsg):
	print("\n[%s] '%s'.\n" % (originalFrame[Ether].src.lower(), decryptedMsg))


class Broker():

	def __init__(self, key=PYEXFIL_DEFAULT_PASSWORD, retFunc=testCallBack):
		"""
		Start the brokering server listener.
		:param server: Server bind addr [str]
		:param port: Listening Port [int]
		:param key: Key for AES-OFB mode. [str]
		:param retFunc: The function to call when a packet comes in.
		:return: None
		"""
		logging.info('Now listening for ARP Broadcasts.')
		logging.info('Hit \'exit\' to quit.')
		self.retFunc = retFunc
		self.key = key

	def parse_message(self, pkt):
		"""
		Start the brokering server listener.
		:param ip: Client IP addr [str]
		:return: None
		"""
		# Here is where you want to hook up to automate communication
		# with the clients.

		if pkt[ARP].op is not 1:
			# Not 'who has?'
			return
		if pkt[Ether].dst.lower() != "ff:ff:ff:ff:ff:ff":
			# Not broadcast
			return

		try:
			# pkt[ARP][Padding].show()
			payload = pkt[ARP][Padding].load

		except:
			pass

		decPayload = AESDecryptOFB(key=self.key, text=payload)

		if self.retFunc is not None:
			self.retFunc(pkt ,decPayload)


	def listen_clients(self):
		while True:
			sniff(prn=self.parse_message, filter="arp", store=0, count=1)


def broadcast_message(message, key=PYEXFIL_DEFAULT_PASSWORD):
	"""
	Send a message over ARP Broadcast
	:param message: Message to send as str.
	:param key: The parameter to use as key.
	:return None:
	"""
	msg = AESEncryptOFB(key=key, text=message)
	n_frame = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(op=1, pdst="192.168.1.254") / Raw(load=msg)
	sendp(n_frame, verbose=False)


if __name__ == '__main__':
	# Make sure all log messages show up

	b = Broker()
	thread.start_new_thread(b.listen_clients, ())
	while True:
		send_me = input("message> ")
		msg = send_me.strip()
		if msg == "":
			continue

		elif msg.strip() == "exit":
			logging.info("Got exit message.\n")
			exit()

		else:
			broadcast_message(msg)
			logging.info("[%s] out the door." % len(msg))
