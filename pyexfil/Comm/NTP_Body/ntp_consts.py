import base64

SERVER      = "127.0.0.1"
NTP_PORT    = 123
KEY         = base64.b64decode('VEhBVElTQURFQURQQVJST1Qh')
RECV_BUFFER = 1024


def _buildNTP():
    """
    Build NTP basic structure.
    :return: Header of NTP[bytes str]
    """
    pyld = "\xd9"  # v3, Symmetric-Active mode
    pyld += "\x00"  # no stratum
    pyld += "\x0a"  # polling every 1024 sec (usually default).
    pyld += "\xfa"  # clock per.
    pyld += "\x00" * 4  # delay
    pyld += "\x00\x01\x02\x90"  # dispersion
    pyld += "\x00" * 4  # refID
    return pyld
