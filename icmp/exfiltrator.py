#!/usr/bin/python
import time
from impacket import ImpactPacket
from socket import *

SLEEP = 0.2
MAX_BYTES_IN_PACKET = 6500
READ_BINARY = "rb"

src = "127.0.0.5"
dst = "127.0.0.1"
FILE_NAME = "1.png"

# Load file
fh = open(FILE_NAME, READ_BINARY)
stri = fh.read()
fh.close()

# Create Raw Socket
s = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)
s.setsockopt(IPPROTO_IP, IP_HDRINCL, 1)

# Create IP Packet
ip = ImpactPacket.IP()
ip.set_ip_src(src)
ip.set_ip_dst(dst)

# ICMP on top of IP 
icmp = ImpactPacket.ICMP()
icmp.set_icmp_type(icmp.ICMP_ECHOREPLY)

# Fragmentation of DATA
x = len(stri) / MAX_BYTES_IN_PACKET								 
y = len(stri) % MAX_BYTES_IN_PACKET								 

seq_id = 0	

# Stream initiation
str_send = FILE_NAME + ":" + str(x+2)
icmp.contains(ImpactPacket.Data(str_send))
ip.contains(icmp)
icmp.set_icmp_id(seq_id)
icmp.set_icmp_cksum(0)
icmp.auto_checksum = 1
s.sendto(ip.get_packet(), (dst, 0))
time.sleep(SLEEP)
seq_id += 1

# Split the file and send it									
for i in range(1,x+2):							 
	str_send = stri[MAX_BYTES_IN_PACKET*(i-1): MAX_BYTES_IN_PACKET*i]				 
	icmp.contains(ImpactPacket.Data(str_send)) # fill ICMP DATA field
	ip.contains(icmp) # encapsulate ICMP packet in the IP packet	 
	seq_id += 1
	icmp.set_icmp_id(seq_id)
	icmp.set_icmp_cksum(0)
	icmp.auto_checksum = 1
	s.sendto(ip.get_packet(), (dst, 0)) # send packet		 
	time.sleep(SLEEP)	

# Add rest of data
str_send = stri[MAX_BYTES_IN_PACKET*i:MAX_BYTES_IN_PACKET*i+ y]
icmp.contains(ImpactPacket.Data(str_send))
ip.contains(icmp)
seq_id += 1
icmp.set_icmp_id(seq_id)
icmp.set_icmp_cksum(0)
icmp.auto_checksum = 1
s.sendto(ip.get_packet(), (dst, 0))
time.sleep(SLEEP)

# Send termination packet
str_send = "\x00\x00\x00\x00"
icmp.contains(ImpactPacket.Data(str_send))
ip.contains(icmp)
seq_id += 1
icmp.set_icmp_id(seq_id)
icmp.set_icmp_cksum(0)
icmp.auto_checksum = 1
s.sendto(ip.get_packet(), (dst, 0))
time.sleep(SLEEP)
sys.stdout.write("Send all packets successfully!\n")