# PyExfil

## Abstract
This started as a PoC project but has later turned into something a bit more. Currently it's an Alpha-Alpha stage package, not yet tested (and will appriciate any feedbacks and commits) designed to show several techniques of data exfiltration is real world scenarios. Currently here are what the package supports and what is allows is:

* DNS query.
* HTTP Cookie.
* ICMP (8).
* NTP requests.
* BGP Open.

Package is still not really usable and will provide multiple issues. Please wait for a more reliable version to come along. 
The release of Symantec's Regin research was the initiator of this module. It is inspired by some of the features of [Regin](http://www.symantec.com/connect/blogs/regin-top-tier-espionage-tool-enables-stealthy-surveillance). Go read about it :)

## Techniques

### DNS
This will allow establish of a listener on a DNS server to grab incoming DNS queries. It will then harvest them for files exfiltrated by the client. It **does not** yet allow simultaneous connections and transfers. DNS packets will look good to most listeners and *Wireshark* and *tcpdump* (which are the ones that have been tested) will show normal packet and not a 'malformed packet' or anything like that.
### HTTP Cookie
Exfiltration of files over HTTP protocol but over the Cookies field. The strong advantage of this is that the cookie field is supposed to be random noise to any listener in the middle and therefore is very difficult to filter. 
### ICMP
Uses ICMP 8 packets (echo request) to add a file payload to it. It reimplemented ICMP ping requests and some sniffers are known to capture it as malformed packets. Wireshark currently displays it as a normal packet. 

## Future Stuff
### Version Alpha
- [ ] Check why HTTP Cookie exfiltration keeps failing CRC checks.
- [X] Add NTP exfiltration. (Thanks to barachy for the idea)
- [X] Complete NTP listener.
- [X] BGP Data exfiltration + listener.
- [ ] Write a proper Documentation.
- [ ] Fix that poorly written *setup.py*.
- [ ] More QA needed and fast!

### Version Beta
- [ ] Enable simultaneous support for all data exfiltration methods. 
- [ ] Translate module to C Windows.
- [ ] Translate module to C Linux.
- [ ] Get a damn logo :)

## Thanks
Thanks [Wireshark](http://wireshark.com/) for your awesome wiki and tool. Especially [packet dumps](http://wiki.wireshark.org/SampleCaptures).
Thanks to barachy and AM for ideas on protocols to use. 
