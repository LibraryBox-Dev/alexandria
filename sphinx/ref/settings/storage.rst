Storage
*******

There are three modes for storage in AlexandriaL

* USB (default) which attaches the first usb disk that is attached to the system as the main storage location
* internal, which lets a specific device be the device that is loaded as the storage location
* manual, which turns off all automounting and ignores the locations. allowing more complicated configurations to be used.

The default is USB, and there are a few requriements for USB devices in this case. Devices which are to be used for USB content hosting
must be:

* Formatted exfat or FAT32
* Have only one partition (if they have multiples, those will be ignored) 


The devices will be mounted by the alexandria interface with the options ```sync,rw,noatime,nosuid,noexec```. This can be changed in the configuration file.


