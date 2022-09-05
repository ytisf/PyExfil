#!/usr/bin/env python3

import sys
import zlib

from pyexfil.includes.prepare import rc4, DEFAULT_KEY
from dev_zone.Bip39EmailPrinter.bip39_encode import BIP_DICTIONARY, build_dictionary, BIP_REVERSE_DICTIONARY


def Load(f_name : str = None):
    if f_name is None:
        try:
            f_name = sys.argv[1]
        except:
            print("Usage: python3 bip39_decode.py <file>")
            exit(1)

    # Build dictionary
    build_dictionary()

    # Read file
    try:
        f = open(f_name, "r").read()
    except Exception as e:
        print("Error: Could not open file")
        print(e)
        exit(1)
    
    # Encrypt and compress
    f = zlib.compress(f.encode())
    # f = rc4(f, DEFAULT_KEY)

    # Convert to hex string
    f = f.hex()

    # If length of data cannot be evenly divided by 4
    # pad with 0's
    if len(f) % 4 != 0:
        f = f.ljust(len(f) + (4 - len(f) % 4), '0')
    
    # Split into 4 byte chunks
    f = [f[i:i+4] for i in range(0, len(f), 4)]

    # Convert to words
    f = [BIP_REVERSE_DICTIONARY[word] for word in f]
    return ' '.join(f)
    

def Decode(data: str):
    # Split into words
    data = data.split(' ')

    # Convert to hex
    data = [BIP_DICTIONARY[word] for word in data]

    # Convert to bytes
    data = bytes.fromhex(''.join(data))

    # Decompress and decrypt
    # data = rc4(data.decode(), DEFAULT_KEY)
    data = zlib.decompress(data)

    return data