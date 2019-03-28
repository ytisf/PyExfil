#!/usr/bin/env python2.7

import sys
import ssl
import random
import socket

try:
	from PyExfil.pyexfil.Comm.DNSoTLS.constants import *
except ImportError:
	# In case you're running it from SA directory
	from constants import *

context = None


def AutomateMe(data, sslSocket):
    """
    This is where you automate me.
    :param data: data that came in [str]
    :param sslSocket: Client SSL Socket Object [ssl wrapper socket object]
    :return: None
    """
    # Caught it!
    # Put your automation here. Notice if you have a lot of computation you might
    # want to go back to line 48 and put this as a thread so not to get a
    # timeout on the client side or backlog other clients here.
    return


def StartServer(server_name=LOCAL_HOST, port=DNS_OVER_TLS_PORT, clients=MAX_CLIENTS, certfile=CERT_FILE, keep_ratio=True):
    """
    Start the server.
    :param server_name: IP of server [str]
    :param port: Port of server [int]
    :param clients: Max amount of clients to allow connections from [5, int]
    :param certfile: Path to certificate to use [str]
    :param keep_ratio: Flag on keeping ration of download:upload data [True, bool]
    :return: Check-Flag [bool]
    """

    global context

    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

    try:
        context.load_cert_chain(certfile=CERT_FILE)
    except Exception as e:
        sys.stderr.write("[!]\tError opening the certificate file '%s'.\n%s.\n" % (CERT_FILE, str(e)))
        return False

    try:
        bind_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        bind_sock.bind((server_name, port))
        bind_sock.listen(clients)
    except Exception as e:
        sys.stderr.write("[!]\tError listening on socket.\n%s.\n" % str(e))
        return False

    while True:
        try:
            newsocket, fromaddr = bind_sock.accept()
            sslsoc = context.wrap_socket(newsocket, server_side=True)
            data = sslsoc.read()
            AutomateMe(data=data, sslSocket=sslsoc)
            if keep_ratio:
                # Sending random data just to make sure we meet the same ratio of
                # response to queries.
                sslsoc.send(str(random.getrandbits(random.randint(8, CHUNK_SIZE))))
            ip,port = newsocket.getpeername()
            sys.stdout.write("\t[%s:%s] '%s'.\n" % (ip, port, data))

        except KeyboardInterrupt:
            sys.stdout.write("\n[!]\tGot a CTRL+C. Exiting now.\n")
            return True

        except socket as e:
            sys.stderr.write("Caught an unknown socket exception. Making sure to kill the socket.\n")
            sys.stderr.write("%s.\n" % str(e))
            bind_sock.close()
            return False


if __name__ == "__main__":
    StartServer()
