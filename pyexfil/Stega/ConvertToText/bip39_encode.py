#!/usr/bin/env python3

import os
import struct
import itertools

BIP_WORDLIST_NAME = "dictionary.txt"
BIP_WORDLIST = os.path.join(os.path.dirname(__file__), BIP_WORDLIST_NAME)
BIP_DICTIONARY = {}
BIP_REVERSE_DICTIONARY = {}


def build_dictionary():
    global BIP_DICTIONARY
    global BIP_REVERSE_DICTIONARY

    try:
        wordlist = open(BIP_WORDLIST, "r").readlines()
    except:
        print("Error: Could not open wordlist")
        exit(1)

    # strip whitespace
    wordlist = [word.strip() for word in wordlist]

    # Generate list of all possible 4 byte combinations
    # 0x00000000 - 0xFFFFFFFF
    for idx, hexstr in enumerate(range(0, len(wordlist))):
        # Convert to hex string
        hex_str = hex(hexstr)[2:].zfill(4)
        # Add to dictionary
        BIP_DICTIONARY[wordlist[idx]] = hex_str
        BIP_REVERSE_DICTIONARY[hex_str] = wordlist[idx]
    
    # Confirm minimum length
    if len(BIP_DICTIONARY) < 65536:
        print("Error: Wordlist too short")
        exit(1)

    return True


build_dictionary()
