import os

DNS_OVER_TLS_PORT = 853
CHUNK_SIZE = 128
CHECK_CERT = True  # We recommend using valid certificates. An invalid certificate (self-signed) might trigger alerts on some systems.
LOCAL_HOST = "localhost"
MAX_BUFFER = 4096
MAX_CLIENTS = 5

if os.getcwd() == "DNSoTLS":
    CERT_FILE = "cert.ccc"
elif os.getcwd() == "PyExfil":
    CERT_FILE = "pyexfil/Comm/DNSoTLS/cert.ccc"
else:
    CERT_FILE = "pyexfil/Comm/DNSoTLS/cert.ccc"
