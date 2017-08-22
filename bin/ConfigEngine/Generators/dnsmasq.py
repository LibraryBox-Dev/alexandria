from ConfigEngine import toBool,writeLines
from ConfigEngine.Generators import engine

@engine.assertConfig("general",["hostname"])
@engine.assertConfig("service.dnsmasq", [ 
    "enabled",
    "interface",
    "start_address",
    "end_address",
    "subnet_mask",
    "lease_time"
    ])
@engine.generator("DNSMasq DHCP and DNS server")
def dnsmasq(buffer):

    dnsmasq_opts = engine.getSection("service.dnsmasq")
    if not toBool(dnsmasq_opts["enabled"]):
        return



    # If you're wondering why this looks bad, it's because it is.
    # Apple is terrible and should feel bad.
    # see VVVVVVVV THIS STACK OVERFLOW ANSWER
    # https://apple.stackexchange.com/questions/62870/how-do-i-tell-an-ios-device-theres-no-internet-connection-on-the-wifi/62905#62905
    # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    # Apparently, if you set the default route to 0.0.0.0 then iOS gets confused and doesn't freak out????
    #
    # dhcp-option=15 sends an empty "domain" entry. This is another attempt to pull the wool over Apple's eyes.

    writeLines(buffer,[
        "interface={0}".format(dnsmasq_opts["interface"]),
        "dhcp-range={start_address},{end_address},{subnet_mask},{lease_time}".format_map(dnsmasq_opts),
        "dhcp-option=3,0.0.0.0",
        "dhcp-option=15"
        ])

    # we need to get the IP address of the interface.
    # we also should make sure that the interface isn't set up for DHCP.

    # Check that the section for the interface exists

    if not engine.hasSection("interface."+dnsmasq_opts["interface"]):
        raise ValueError("Interface for dnsmasq is not defined.")
    if not engine.hasOption("interface."+dnsmasq_opts["interface"], "dhcp") or engine.getOption("interface."+dnsmasq_opts["interface"],"dhcp",toBool):
        raise ValueError("Interface for dnsmasq does not define DHCP option or is configured for dhcp")
    # we want the IP address of the interface.
    ipAddr = engine.getOption("interface."+dnsmasq_opts["interface"], "ip")
    writeLines(buffer, ["address=/{0}/{1}".format(
        engine.getOption("general","hostname")+"."+engine.getOption("general","tld"),
        ipAddr
        )
    ])
    pass

