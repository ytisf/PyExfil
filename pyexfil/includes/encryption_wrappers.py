from Crypto.Cipher import AES
import base64


mode 						= AES.MODE_OFB
iv 							= "\x00" * 16
PYEXFIL_DEFAULT_PASSWORD 	= base64.b64decode('VEhBVElTQURFQURQQVJST1Qh')



""" START Symmetric stream mode for AES """

def AESEncryptOFB(key, text):
	pad_len = (-len(text)) % 16
	padded_text = text + ("\x00" * pad_len)
	padded_key = key + ("\x00" * (32 - len(key)))
	encs = AES.new(padded_key, mode, iv)
	plain = encs.encrypt(padded_text)
	return plain

def AESDecryptOFB(key, text, unpad=True):
	padded_key = key + ("\x00" * (32 - len(key)))
	decryptor = AES.new(padded_key, mode, iv)
	plain = decryptor.decrypt(text)
	if unpad:
		plain = plain.replace("\x00", '')
	return plain

""" END Symmetric stream mode for AES """
