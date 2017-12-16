import sys
from scapy.all import *

BSSID_NAME  = "pyExfil"
MAX_SIZE    = 65000
ADAPTER     = "en2"
DELIMITER   = "\x00\xFF\x00\xFF" # Using this delimiter since after compression and encryption
                                 # chars should not be repeating like this.
ADDR1       = "00:00:00:00:00:42"
ADDR2       = "00:00:00:00:00:42"
ADDR3       = "00:00:00:00:00:42"

class Dot11EltRates(Packet):
    """ Our own definition for the supported rates field """
    name = "802.11 Rates Information Element"
    # Our Test STA supports the rates 6, 9, 12, 18, 24, 36, 48 and 54 Mbps
    supported_rates = [0x0c, 0x12, 0x18, 0x24, 0x30, 0x48, 0x60, 0x6c]
    fields_desc = [ByteField("ID", 1), ByteField("len", len(supported_rates))]
    for index, rate in enumerate(supported_rates):
        fields_desc.append(ByteField("supported_rate{0}".format(index + 1),
                                     rate))

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
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

dataObject = {}

def PacketHandler(pkt) :
    global dataObject
    if pkt.haslayer(Dot11) :
        print "got"
        if pkt.haslayer(Dot11Elt):
            if pkt[Dot11Elt].info == BSSID_NAME and pkt[Dot11].addr1 = ADDR1:
                # check if this is the first packer or not:
                data = pckt.payload.split(DELIMITER)
                if len(data) == 2:
                    # This is a data packet
                    dataObject['data'].append([data[0], data[1]])
                    if data[0] == dataObject['packets']:
                        raw = ""
                        for counter, info in dataObject['data']:
                            raw += info
                        key = "shut_the_fuck_up_donnie!"
                        aesObj = AESCipher(key)
                        try:
                            dec = aesObj.decrypt(raw)
                            f = open("data.dec", 'wb')
                            f.write(dec)
                            sys.stdout.write("Decrypted data was saved to 'data.dec'.\n")
                        except:
                            sys.stdout.write("File could not be decrypted. Saving encrypted data.\n")
                            f = open("encrypted.raw", 'wb')
                            f.write(raw)
                        f.close()
                        dataObject = {}
                    continue
                elif len(data) == 3:
                    # This is an init packet.
                    dataObject['data'] = []
                    dataObject['hash'] = data[1]
                    dataObject['packets'] = data[0]
                    sys.stdout.write("Starting to get %s packets of data for hash %s.\n" % (data[0], data[1]))
                    continue

def StartListening(adapter=ADAPTER):
    sniff(iface=ADAPTER, prn=PacketHandler)
