#!/usr/bin/env python

import logging
import threading
from socket import *

from pyexfil.comm.ntp_body.ntp_consts import *
from pyexfil.includes.encryption_wrappers import AESDecryptOFB, AESEncryptOFB


class Broker:
    def __init__(self, server="", port=NTP_PORT, key=KEY):
        """
        Start the brokering server listener.
        :param server: Server bind addr [str]
        :param port: Listening Port [int]
        :param key: Key for AES-OFB mode. [str]
        :return: None
        """
        logging.info("Initializing Broker")
        self.key = key
        self.sock = socket(AF_INET, SOCK_DGRAM)
        addr = (server, port)
        self.sock.bind(addr)
        self.clients_list = []

    def talkToClient(self, ip):
        """
        Start the brokering server listener.
        :param ip: Client IP addr [str]
        :return: None
        """
        # Here is where you want to hook up to automate communication
        # with the clients.
        logging.info("Sending 'ok' to %s", ip)
        d = _buildNTP()
        d += AESEncryptOFB(key=self.key, text="OK")
        self.sock.sendto(d, ip)

    def listen_clients(self):
        while True:
            msg, client = self.sock.recvfrom(RECV_BUFFER)
            logging.info("Received data from client %s." % str(client))
            decData = AESDecryptOFB(key=self.key, text=msg[-16:])
            logging.info("Decrypted message reads: %s." % decData)
            t = threading.Thread(target=self.talkToClient, args=(client,))
            t.start()


if __name__ == "__main__":
    # Make sure all log messages show up
    logging.getLogger().setLevel(logging.DEBUG)

    b = Broker()
    b.listen_clients()
