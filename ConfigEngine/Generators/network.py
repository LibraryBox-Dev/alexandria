
from ConfigEngine import toBool,writeLines
from ConfigEngine.Generators import engine


@engine.namespace("interface")
@engine.assertConfig(None, [ "type","enabled","dhcp","ip","subnet_mask","gateway" ])
@engine.generator("Debian interface confguration (single interface)",True)
def debian_interface(buffer, iface):

    # If DHCP is enabled, it's simple
    ifacedict = engine.getSection("interface."+iface)

    
    if(toBool(ifacedict["enabled"])):
        print("auto {0}".format(iface),file=buffer)


    if(toBool(ifacedict["dhcp"])):
        # Sanity check: Is this the interface for dnsmasq or hostapd?
        dnsmasq_iface = engine.getOption("network","dnsmasq_interface")
        hostapd_iface = engine.getOption("network","hostapd_interface")
        if(iface == dnsmasq_iface or iface == hostapd_iface):
            raise ValueError("Can't run dnsmasq or hostapd on a dhcp interface.")

        # This is a dhcp interface.
        writeLines(buffer, [
            "allow-hotplug {0}".format(iface),
            "iface {0} inet dhcp".format(iface)
            ])
    else:
        writeLines(buffer, [
            "iface {0} inet static".format(iface),
            "\taddress {0}".format(ifacedict["ip"]),
            "\tnetmask {0}".format(ifacedict["subnet_mask"]),
            ])
        if ifacedict["gateway"] != "":
            writeLines(buffer, ["\tgateway {0}".format(ifacedict["gateway"])])

    # check if it's a wireless interface. 
    
    if( ifacedict["type"] == "wireless" ):
        # it's a wireless interface!
        # if we use wpa, we need to write different options than if it's an open network.
        if ifacedict["mode"] == "ap":
            return
        elif ifacedict["security"] == "none":
            writeLines(buffer,["\twireless-essid {0}".format(ifacedict["ssid"])])
        elif ifacedict["security"] == "wpa":
            writeLines(buffer,[
                "\twpa-ssid {0}".format(ifacedict["ssid"]),
                "\twpa-psk {0}".format(ifacedict["psk"])
                ])
        else:
            raise ValueError("Malformed option value: Unknown security type {0} on section interface.{1}".format(ifacedict["security"],iface))
    # Nothing special here has to be set up for wired connections, so we're done here.


@engine.generator("Debian loopback interface")
def debian_loopback(buffer):
    writeLines(buffer,[
        "auto lo",
        "iface lo inet loopback"
        ])
