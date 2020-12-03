#!/usr/bin/python

import sys
import hashlib

from scapy.all import *

sport = 59943

data_incoming = ""


def pkt_callback(pkt):
    global data_incoming
    if pkt[TCP].sport == sport:
        segments = pkt[IP].src.split(".")
        for segment in segments:
            data_incoming += chr(int(segment))

        if data_incoming[-8:] == chr(255) * 8:
            sys.stdout.write("Got termination bits.\n")
            data = data_incoming
            data = data[:-10] + data[-10:].replace(chr(255), "")
            try:
                write_me = zlib.decompress(data)
                md5_file = hashlib.md5(write_me).hexdigest()
                open("%s.output" % md5_file, "wb").write(write_me)
                sys.stdout.write("Wrote outputfile to %s.output.\n" % md5_file)
                data_incoming = ""
            except:
                sys.stderr.write("Something went wrong with data decompression.\n")
                data_incoming = ""
        else:
            # Packet not matching origin port
            pass


if __name__ == "__main__":
    sniff(iface="en0", prn=pkt_callback, filter="tcp", store=0)
