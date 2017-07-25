HostAPd
*******

Hostapd is a service for generating wireless networks on Linux devices. Alexandria uses it for the configuration of its wireless network.

Settings
========

* Country: A two-letter code for the regulatory area that you plan on using the network in.
* 802.11 Channel: The wireless channel that the network should run on. Wireless networks need to have a bit of separation, as there is overlap between channels 1,2 and 3. For more information, see the `Wikipedia article on 802.11 channels <https://en.wikipedia.org/wiki/List_of_WLAN_channels>`_ for a detailed look. The default, 6, is common and has no overlap with most areas.

.. note:: 
   **What about ```auto```?**
   The reason for auto-channel fields was such that there would be "smart" wireless access points that would pick a channel that was less populated at the time. This evolved into picking the least used channel *at that moment* and changing to it, announcing to connected devices that it was changing channel. While this was fine for not so populous areas, auto-channel changing is noisy and causes a lot of problems with some devices, which cannot handle having the access point change channel more than every so often.

* SSID: The name of the network that the device will use.
* WPA Security: Enabling WPA security hides the traffic on the network to anyone who does not know the passphrase. It's good enough security for most home environments, where it is most commonly seen.
* WPA Passphrase: The passphrase that will be used for WPA encryption.
* Hide SSID: This option disables broadcasting the network as available when clients seek to connect. This will show up on devices as as "hidden network" or be ignored. 

Warning on security
-------------------

The WPA encryption and hiding of an SSID do not make your network attack-proof. There is no true defense against someone finding the name of your network, as many operating systems simply try to announce that they wish to connect to all the networks that they know, one at a time. It has only been in recent years that this practice has changed and a "listen before you connect" approach has been taken.

Hiding your SSID does not stop someone with software like Airsnort, Wireshark or other network sniffing tools from finding the name of your network. The tools needed for this activity are free or cheap, requiring only a laptop and some patience.

Turning on WPA encryption will obscure data being sent via the wireless network only until someone knows the key. There are ways to brute-force keys, especially weak ones, that will reveal the traffic on the network. However, if this is that important to you, consider if you feel that a `US$6 pipe wrench <https://www.harborfreight.com/10-in-steel-pipe-wrench-61465.html>`_ might be enough to `get that information <https://www.xkcd.com/538/>`_ through people who know it. 
