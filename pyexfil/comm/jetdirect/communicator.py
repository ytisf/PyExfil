#!/usr/bin/env python2.7

import logging
import _thread

import socket

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


def testCallBack(src, decryptedMsg):
    print("HEREsdfk")
    print("\n[%s:%s](incoming)\t'%s'.\n" % (src[0], src[1], decryptedMsg))


class Broker:
    def __init__(
        self,
        client,
        host="127.0.0.1",
        port=9100,
        key=PYEXFIL_DEFAULT_PASSWORD,
        retFunc=testCallBack,
    ):
        """
        Start the brokering server listener.
        :param client: Client's IP [str]
        :param server: Server bind addr [str]
        :param port: Listening Port [int]
        :param key: Key for AES-OFB mode. [str]
        :param retFunc: The function to call when a packet comes in.
        :return: None
        """
        logging.info("Now listening for 9100/udp Broadcasts.")
        logging.info("Hit 'exit' to quit.")
        self.retFunc = retFunc
        self.key = key
        self.client = client
        self.port = port
        self.host = host

    def parse_message(self, src, data):
        """
        Start the brokering server listener.
        :param ip: Client IP addr [str]
        :return: None
        """
        # Here is where you want to hook up to automate communication
        # with the clients.

        decPayload = AESDecryptOFB(key=self.key, text=data)

        if self.retFunc is not None:
            self.retFunc(src, decPayload)

    def listen_clients(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        logging.info("Listening on UDP %s:%s" % (self.host, self.port))
        s.bind((self.host, self.port))
        while True:
            (data, addr) = s.recvfrom(128 * 1024)
            self.parse_message(addr, data)

    def broadcast_message(self, message):
        """
        Send a message over ARP Broadcast
        :param message: Message to send as str.
        :param key: The parameter to use as key.
        :return None:
        """
        msg = AESEncryptOFB(key=self.key, text=message)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        sock.sendto(msg, (self.client, self.port))


if __name__ == "__main__":
    # Make sure all log messages show up

    b = Broker(client="127.0.0.1")
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
            b.broadcast_message(msg)
            logging.info("[%s] out the door." % len(msg))
