Installing Alexandria
*********************

From source
===========

Installing Alexandria from source is relatively easy. The default installer
makes the assumption that you're running on a Debian-based system. If you are
not running on Debian, you will need to make sure to have the closest equivalent
packages as listed in the installer script.

To install on a Debian based system, simply

 * get a copy of the repository from git and put it somewhere like ``/opt/alexandria``

.. note: This location will be set in stone to some degree. You will need to edit ``/etc/alexandria-env`` if something changes.

 * run install.sh as root
 * you're now ready to go

.. warning: This will disable certain systemd units. If you do not wish to have systemd units
           modified, then you WILL have to modify the installer script in order to avoid this.

.. note: Alexandria's installer assumes you are running the Alexandria as the primary service of
        the device. If this is not the case, please see the section "Running the librarian on its own"

From prepared SD cards
======================

.. note: Prepared SD cards are intended for use with the Raspberry Pi 3. While it is possible to run
        the prepared Alexandria installation on a Raspberry Pi 2, it is not suggested and may have
        performance issues. This is not currently supported or suggested.

Installing from a prepared SD card is the most common mechanism. To do so, it is recommended you use
`Etcher <http://etcher.io>`_ for writing SD card images.

.. warning: This process **erases** any content you have on the SD card.

.. warning: **Etcher will make every attempt to not overwrite your system's disk**, however it will
           erase the content of any USB disk you point it at. Double check *all* 

You will need:

* An SD card of at least 4GB in size
* A Raspberry Pi 3
* Etcher

* Make sure you have Etcher open and your SD card inserted and visible to your computer
* Select the Alexandria SD card image
* Choose your SD card from the list.
* Press go
* Sit back, relax, let it go.

.. note: Windows will helpfully try and pop up a series of dialogs during this process. These
        include a message stating that the disk is not formatted. Ignore these dialogs, closing
        them. It is advised to leave your computer alone during this time and wait until the
        process has finished.

For Linux users, if you aren't interested in installing another utility, you're going to need
to unzip the alexandria archive, then use::

    dd if=<path to decompressed image> of=<path to your SD card> BS=1M

If your computer has an SD card reader built in, it is likely you want ``/dev/mmcblk0``. In all cases,
you want the whole device. If your card reader comes up as a USB disk (not an MMC device), you will
likely want a device named ``/dev/sdc``. use::

    watch 'dmesg | tail'

to watch the very end of the message log. Inserting and removing your device should show
something like::

    [606741.531369] usb 2-1: new SuperSpeed USB device number 2 using xhci_hcd
    [606741.555102] usb 2-1: New USB device found, idVendor=1f75, idProduct=0917
    [606741.555112] usb 2-1: New USB device strings: Mfr=1, Product=2, SerialNumber=3
    [606741.555118] usb 2-1: Product: USB 3.0
    [606741.555123] usb 2-1: Manufacturer:  innostor
    [606741.555128] usb 2-1: SerialNumber: 201207224131
    [606741.971604] usb-storage 2-1:1.0: USB Mass Storage device detected
    [606741.971917] scsi host1: usb-storage 2-1:1.0
    [606741.973600] usbcore: registered new interface driver usb-storage
    [606742.001424] usbcore: registered new interface driver uas
    [606742.996637] scsi 1:0:0:0: Direct-Access     IS917                     1.00 PQ: 0 ANSI: 6
    [606742.997978] sd 1:0:0:0: Attached scsi generic sg1 type 0
    [606742.998288] sd 1:0:0:0: [sdb] 31457280 512-byte logical blocks: (16.1 GB/15.0 GiB)
    [606742.998465] sd 1:0:0:0: [sdb] Write Protect is off
    [606742.998474] sd 1:0:0:0: [sdb] Mode Sense: 23 00 00 00
    [606742.998647] sd 1:0:0:0: [sdb] Write cache: disabled, read cache: disabled, doesn't support DPO or FUA
    [606743.002989]  sdb: sdb1
    [606743.004315] sd 1:0:0:0: [sdb] Attached SCSI removable disk

Here, the important bit is ``sdb``: that's the device name.

Creating SD card images
=======================

.. note: this section is intended for the brave at heart. This process will generate a working raspberry pi
        disk image.

You will need:

* A Raspbian disk image
* the following packages: ``systemd-nspawn``, ``zip``, ``losetup``, ``qemu-user-static``, ``binfmt-support``.

.. note: You are not required to use the static version of qemu-user, but it will make your life easier.

The tool ``make-pi-image.sh`` is used for this typically. This will potentially work on any ARM-based system
that looks like Raspbian and which has /boot on its own partition. Adjust for your target. 