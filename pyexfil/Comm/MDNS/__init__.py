import struct

from scapy.all import Raw, UDP, IP, send

MDNS_PORT = 5353
TEST_QUERY = "main_zone_tcp.local"


def Send (dst_ip, data, sequence=0, spoof_source=False, dst_port=MDNS_PORT, src_port=MDNS_PORT, dns_name=TEST_QUERY):
	"""
	Send one packet of MDNS with data.
	:param dst_ip: IP as string.
	:param data: Data as bytes/string.
	:param sequence: Number to use for sequence. Int.
	:param spoof_source: Default:False. Set as IP for spoofing.
	:param dst_port: ....
	:param src_port: ...
	:param dns_name: DNS name to put in the MDNS request.
	:return: semper vera!!!
	"""
	payload = ""
	payload += "\x00"  # TransID is 2 bytes. Using one for sequence.
	payload += struct.pack('B', sequence)
	
	payload += "\x00\x00"  # Stndrt qry
	payload += "\x00\x01"  # 1 questions
	payload += "\x00\x00"  # 0 ans RRs
	payload += "\x00\x00"  # 0 authority RRs
	payload += "\x00\x00"  # 0 additional RRs
	# Start of query:
	payload += struct.pack('B', len(dns_name))  # Length? -> YES it is!
	payload += dns_name  # name
	payload += "\x00"  # Query Terminator
	payload += "\x00\x0c"  # PTR request
	payload += "\x00\x01"  # class IN
	
	if spoof_source is False:
		pkt = IP(
				dst = dst_ip
				# src = "1.1.1.1"
		) / UDP(
				sport = src_port,
				dport = dst_port
		) / Raw(
				load = payload
		)
	else:
		pkt = IP(
				dst = dst_ip,
				src = spoof_source
		) / UDP(
				sport = src_port,
				dport = dst_port
		) / Raw(
				load = data
		)
	send(pkt)
	return True

