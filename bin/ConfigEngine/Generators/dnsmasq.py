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




    # https://github.com/TowCenter/YouAreHere/blob/master/install.sh#L196
    # According to this, sinkholing apple.com will fix the problem.
    # 
    writeLines(buffer,[
        "interface={0}".format(dnsmasq_opts["interface"]),
        "dhcp-range={start_address},{end_address},{subnet_mask},{lease_time}".format_map(dnsmasq_opts),
        "address=/apple.com/0.0.0.0",
        "domain-needed",
        "bogus-priv",
        "domain=",
        "server=0.0.0.0"
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

