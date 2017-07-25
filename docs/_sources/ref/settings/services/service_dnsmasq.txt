DNSMasq
*******

DNSMasq is a DNS server and DHCP server. It is responsible for handing out IP addresses of things, including the address for your Alexandria device.

You shouldn't have to configure much in DNSMasq, but you will need to change a few things in the event you do wish to change how it works.

Settings
========

* Starting IP: The first IP that DNSMasq will hand out via DHCP
* Ending IP: The last IP that DNSMasq will hand out via DHCP
* Subnet mask: The subnet mask that DNSMasq will hand to devices via DHCP
* Lease time: The amount of time, in minutes, that a device will be able to retain its assigned IP address before needing to request a new one.

.. note:: A long lease time means that if there are a large number of devices, devices which have disconnected still have a ticking lease timer. A short lease time (typically 20) is good if you plan on having a large number of devices that connect and disconnect on a regular basis.


