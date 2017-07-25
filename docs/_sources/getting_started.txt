Getting Started with Alexandria
*******************************

Welcome to Alexandria. This guide will get you started on the first steps on getting an alexandria-enabled device up and going.

If you're starting with a device with Alexandria preinstalled, you're in the right place. Otherwise, look at the `Installing Alexandria <install.rst>`_.

Your first steps
================

All changes in alexandria only take effect once the device is restarted, to prevent accidential changes from causing instant regret.

Setting the admin password
--------------------------

The first thing you'll want to do is make sure to change the passphrases used for administration. Alexandria does not have any means to separate users, and as a result, there is one single password that grants authentication to the administrative interface.

Your Alexadria device should come up as a wireless network. Connect to that network and navigate to the Alexandria front page typically at http://alexandria.lan/ (Check with the documentation of your device's version of Alexandeia, as this might have been changed.)

Click the administration link in the menu and present the default passphrase: ```librarian```. Then, change the passphrase under "General Settings". Press save and follow the prompt to restart your device.

Choosing storage
----------------

The second thing you'll need to do is determine what kind of storage you'll use. By default, Alexandria uses the first USB device that is plugged in for storage. If there are multiple partitons on that USB storage device, all but the first will be ignored. Alexandria also supports using a part of the internal storage for this purpose. To choose between these options, select "Storage" in the administration panel of Alexandria.

Some people are okay with messing with their device directly. In that case, there is a manual setting for storage.

Securing the wireless network
-----------------------------

Sometimes, an open network is not an option. There are two options that can be changed to lock down or otherwise hide the network.

First, Alexandria supports adding a layer of security known as "WPA PSK". This means that devices that don't know the passphrase (or "pre-shared key") to the network cannnot connec to it. However, those who do are able to see traffic on the network. Second, Alexandria can be configured to not send "broadcast" details about the network, requiring devices to know the name of the network.

WPA security is good enough for the average situation. Not broadcasting the network information is only a certain amount of obscurity; anyone with a wireless sniffing software can listen for connections to ssids that aren't broadcasting, then get the name of the network by seeing if there was a response.


