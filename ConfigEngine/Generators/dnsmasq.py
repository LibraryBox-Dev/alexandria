from ConfigEngine import toBool,writeLines
from ConfigEngine.Generators import engine

@engine.assertConfig("general",["hostname"])
@engine.assertConfig("network", [ 
    "dnsmasq_enable",
    "dnsmasq_interface",
    "dnsmasq_start_address",
    "dnsmasq_end_address",
    "dnsmasq_subnet_mask",
    "dnsmasq_lease_time"
    ])
@engine.generator("DNSMasq DHCP and DNS server")
def dnsmasq(buffer):

    network = engine.getSection("network")
    if not toBool(network["dnsmasq_enable"]):
        return

    writeLines(buffer,[
        "interface={0}".format(network["dnsmasq_interface"]),
        "dhcp-range={dnsmasq_start_address},{dnsmasq_end_address},{dnsmasq_subnet_mask},{dnsmasq_lease_time}".format_map(network),
        "local=/{0}/".format(engine.getOption("general","tld")),
        "dhcp-option=3"
        ])

    # we need to get the IP address of the interface.
    # we also should make sure that the interface isn't set up for DHCP.

    # Check that the section for the interface exists

    if not engine.hasSection("interface."+network["dnsmasq_interface"]):
        raise ValueError("Interface for dnsmasq is not defined.")
    if not engine.hasOption("interface."+network["dnsmasq_interface"], "dhcp") or engine.getOption("interface."+network["dnsmasq_interface"],"dhcp",toBool):
        raise ValueError("Interface for dnsmasq does not define DHCP option or is configured for dhcp")
    # we want the IP address of the interface.
    ipAddr = engine.getOption("interface."+network["dnsmasq_interface"], "ip")
    writeLines(buffer, ["address=/{0}/{1}".format(
        engine.getOption("general","hostname")+"."+engine.getOption("general","tld"),
        ipAddr
        )])
    pass

