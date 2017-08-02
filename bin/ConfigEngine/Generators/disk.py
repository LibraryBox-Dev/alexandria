from ConfigEngine.Generators import engine
import sys

@engine.generator("Mount environment generator")
def mounts(stream):
    # The following things need to be hauled out:
    # * storage.mode (usb,part,manual)
    # * storage.device (usb -> "/dev/usbstor", part -> read, manual-> None )
    # * storage.mountpoint (default is something like /media/storage or someting?)

    # We need to generate three environment variables:
    # MOUNTPOINT = where to mount the filesystem
    # DEVICE     = the device to mount
    # MODE       = manual or auto

    storage = engine.getSection("storage")
    if(storage["mode"] == "manual"):
        print("MODE=manual",file=stream)
        return
    else:
        print("MODE=auto",file=stream)
        print("MOUNTOPTS={0}".format(storage["options"]),file=stream)
        print("MOUNTPOINT={0}".format(storage["location"]),file=stream)
        dev = storage["device"]
        if(storage["mode"] == "usb"):
            dev = storage["usb_device"]
        print("DEVICE={0}".format( dev ), file=stream)

    pass
   
