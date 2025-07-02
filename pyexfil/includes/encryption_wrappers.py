from Crypto.Cipher import AES
import base64
import hmac
import hashlib

mode 						= AES.MODE_OFB
iv 							= "\x00" * 16
PYEXFIL_DEFAULT_PASSWORD 	= base64.b64decode('VEhBVElTQURFQURQQVJST1Qh')


""" Create HMAC Digest """
def GenerateHMAC(data, key=PYEXFIL_DEFAULT_PASSWORD):
	"""
	Create an HMAC digest using the SHA-256 hash algorithm.

	Parameters:
		data (bytes): Data to be hashed.
		key (bytes): Secret key used for HMAC generation.

	Returns:
		bytes: HMAC digest of the data.
	"""
	return hmac.new(key, data, hashlib.sha256).digest()


def VerifyHMAC(data, expected_hmac, key=PYEXFIL_DEFAULT_PASSWORD):
	"""
	Verify an HMAC digest.

	Parameters:
		data (bytes): Original data whose HMAC was generated.
		expected_hmac (bytes): HMAC digest to verify.
		key (bytes): Secret key used for HMAC generation.

	Returns:
		bool: True if verification is successful, False otherwise.
	"""
	# Generate a new HMAC digest from the data and key
	new_hmac = GenerateHMAC(data, key)
	# Compare the new HMAC with the expected HMAC
	return hmac.compare_digest(new_hmac, expected_hmac)



""" START Symmetric stream mode for AES """

def AESEncryptOFB(key, text):
	if type(key) == str:
		key = bytes(key, 'ascii')
	pad_len = (-len(text)) % 16
	padded_text = text + b'\x00' * pad_len
	padded_key = key +  b'\x00' * (32 - len(key))
	encs = AES.new(padded_key, mode, iv.encode("utf8"))
	plain = encs.encrypt(padded_text)
	return plain

def AESDecryptOFB(key, text, unpad=True):
	if type(key) == str:
		key = bytes(key, 'ascii')
	padded_key = key + b'\x00' * (32 - len(key))
	decryptor = AES.new(padded_key, mode, iv.encode("utf8"))
	plain = decryptor.decrypt(text)
	if unpad:
		plain = plain.replace(b'\x00', b'')
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
