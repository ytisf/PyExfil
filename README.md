# PyExfil
Stress Testing Detection & Creativity

[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=round)](https://github.com/ytisf/PyExfil/issues)
[![HitCount](http://hits.dwyl.com/ytisf/PyExfil.svg)](http://hits.dwyl.com/ytisf/PyExfil)
[![PyPI download month](https://img.shields.io/pypi/dm/ansicolortags.svg)](https://pypi.python.org/pypi/pyexfil/)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/pyexfil/)
[![GitHub stars](https://img.shields.io/github/stars/ytisf/PyExfil.svg?style=social&label=Star&maxAge=2592000)](https://GitHub.com/ytisf/PyExfil/stargazers/)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

![Logo](https://www.morirt.com/img/PyExfil_Logo.png)

PyExfil was born as a PoC and kind of a playground and grew to be something a bit more. In my eyes it's still a messy PoC that needs a lot more work and testing to become `stable`. The purpose of PyExfil is to set as many exfiltration, and now also communication, techniques that **CAN** be used by various threat actors/malware around to bypass various detection and mitigation tools and techniques. You can track changes at the official [GitHub page](https://PyExfil.MoriRT.com/).

Putting it simply, it's meant to be used as a testing tool rather than an actual Red Teaming tool. Although most techniques and methods should be easily ported and compiled to various operating systems, some stable some experimental, the transmission mechanism should be stable on all techniques. Clone it, deploy on a node in your organization and see which systems can catch which techniques.

## Getting Started

### PIP
For using `pip` (not necessarily the most updated):
```bash
pip install --user PyExfil
```

### Prerequisites
For source:
```bash
git clone https://www.github.com/ytisf/PyExfil
cd PyExfil
pip install --user -r requirements.txt
```

We recommend installing [`py2exe`](http://www.py2exe.org/) as well so that you may cross compile various modules to a binary for easier transportation. You can do that with:

```bash
pip install py2exe
```

### Installing

Go to the same folder where `PyExfil` was cloned to and:
```bash
pip setup.py --user install
```

## List of Techniques

* **Network**
  * [DNS query](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#dns-query)
  * [HTTP Cookie](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#http-cookies)
  * [ICMP (8)](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#icmp-echo-8)
  * [NTP Body](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#ntp-body)
  * [BGP Open](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#bgp-open)
  * [HTTPS Replace Certificate](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#https-replace-certificate)
  * [QUIC - No Certificate](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#quic)
  * [Slack Exfiltration](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#slack)
  * [POP3 Authentication](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#pop3-authentication) (as password) - Idea thanks to [Itzik Kotler](https://github.com/ikotler)
  * [FTP MKDIR](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#ftp-mkdir) - Idea thanks to [Itzik Kotler](https://github.com/ikotler)
  * [Source IP-based Exfiltration](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#source-ip-based-exfiltration)
  * [HTTP Response](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#http-response)
* **Communication**
  * [NTP Request](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#ntp-request)
  * [DropBox LSP](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#dropbox-lsp) (Broadcast or Unicast)
  * [DNS over TLS](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#dns-over-tls)
  * [ARP Broadcast](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#arp-broadcast)
  * [JetDirect](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#jetdirect)
  * [GQUIC](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#gquic) - [Google Quick UDP](https://www.chromium.org/quic) Internet Connections (Client Hello)
  * [MDNS Query](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#mdns-query) - *Can be used as broadcast.*
  * [AllJoyn](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#alljoyn). Name Service Protocol (IoT discovery) Version 0 ISAT.
  * [PacketSize](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#packet-size). Using size of packet rather than actual data.  
* **Physical**
  * [Audio](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#audio) - *No listener*.
  * [QR Codes](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#qr-codes)
  * [WiFi - On Payload](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#wifi-frame-payload)
* **Steganography**
  * [Binary Offset](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#image-binary-offset)
  * [Video Transcript to Dictionary](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#video-dictionary)
  * [Braille Text Document](https://github.com/ytisf/PyExfil/blob/master/USAGE.md#braille-text-document)

For usage per modules have a look at the [USAGE](https://www.github.com/ytisf/PyExfil/USAGE.md) file.

## Data Generation
Although this tool was initially created as a game and later on turned to be a Red Team oriented tool, at the end of a day a major usage of `PyExfil` is to test various DLP (Data Leakage Protection) systems as well as detection of intrusion. To make the latter mission simpler we have created a little module to generate fake data with a structure that matches both PII and PCI data sets. These are intended to trigger alerts while being broadcated outside of the network.

Here is how to use it:
```python
from pyexfil.includes import CreateTestData

c = CreateTestData(rows=1000, output_location="/tmp/list.csv")
c.Run()
```

After this you can use which ever `PyExfil` module you would like to try and exfiltrate the data set created. This way you can test your detection without risking exfiltrating valuable data.


## Contributions

We welcome it! From testing, to improving quality of code and up to entirely new methods.

## Future Changes

### Versioning
For details about version look at the [tags on this repository](https://www.github.com/ytisf/PyExfil/tags).

### Version 1.0.0!
- [x] Surprise on restructure (Add Another).
- [x] Split `DOCUMENTATION.md` and `README.md` to two different files.
- [x] Get a nice logo.
- [x] Uniform calling convention for newer modules.
- [x] Exfiltration data-set generator (PII&PCI).

### Version 1.1.0:
- [ ] Review older modules and convert to newer.
- [ ] Add servers to come modules.

### Hopefully - Close Future
- [ ] Attempt at creating a more uniform call convention.
- [ ] Fix that poorly written *setup.py*.
- [ ] Backport all old modules to new calling convention.

### In the Distant Future - The Year 2000
- [ ] Add Golang/C++ support for portability.
- [ ] Extensive testing for py2exe support.

## Acknowledgments

### People & Companies
- Big shout out to [JetBrains](https://www.jetbrains.com/)!!!
- Thanks to barachy and AM for ideas on protocols to use.
- Thanks to [Itzik Kotler](https://github.com/ikotler) for some ideas.

### Resources
- Thanks [Wireshark](https://wireshark.com/) for your awesome wiki and tool. Especially [packet dumps](http://wiki.wireshark.org/SampleCaptures).
- Shout out to the [nmap](https://nmap.org/) guys.
- Thanks to [Trey Hunner](https://github.com/treyhunner) for the package [`names`](https://github.com/treyhunner/names).
- The [Faker](https://faker.readthedocs.io/en/master/) package.
- Special thanks to Thomas Baruchel and Fredrik de Vibe for the [txt2pdf](https://github.com/baruchel/txt2pdf) package we used in the `braille` exfiltration package.
