from Crypto.Cipher import AES
import base64


mode = AES.MODE_OFB
iv = "\x00" * 16
PYEXFIL_DEFAULT_PASSWORD = base64.b64decode("VEhBVElTQURFQURQQVJST1Qh")


""" START Symmetric stream mode for AES """


def AESEncryptOFB(key, text):
    pad_len = (-len(text)) % 16
    padded_text = text + b"\x00" * pad_len
    padded_key = key + b"\x00" * (32 - len(key))
    encs = AES.new(padded_key, mode, iv)
    plain = encs.encrypt(padded_text)
    return plain


def AESDecryptOFB(key, text, unpad=True):
    padded_key = key + b"\x00" * (32 - len(key))
    decryptor = AES.new(padded_key, mode, iv)
    plain = decryptor.decrypt(text)
    if unpad:
        plain = plain.replace(b"\x00", b"")
    return plain


""" END Symmetric stream mode for AES """


""" RC4 START """
# https://github.com/bozhu/RC4-Python/blob/master/rc4.py
def KSA(key):
    keylength = len(key)
    S = range(256)
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % keylength]) % 256
        S[i], S[j] = S[j], S[i]  # swap
    return S


def PRGA(S):
    i = 0
    j = 0
    while True:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]  # swap
        K = S[(S[i] + S[j]) % 256]
        yield K


def RC4_unwrapped(key):
    S = KSA(key)
    return PRGA(S)


def RC4(key, plaintext):
    def convert_key(s):
        return [ord(c) for c in s]

    key = convert_key(key)
    keystream = RC4_unwrapped(key)

    data = ""
    for c in plaintext:
        data += "%02X" % (ord(c) ^ keystream.next())


""" RC4 Ends """
