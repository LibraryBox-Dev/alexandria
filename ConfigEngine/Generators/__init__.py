from ConfigEngine import ConfigEngine, toBool, writeLines

engine = ConfigEngine()

__all__ = []

import pkgutil
import inspect

for loader, name, is_pkg in pkgutil.walk_packages(__path__):
    module = loader.find_module(name).load_module(name)

    for name, value in inspect.getmembers(module):
        if name.startswith('__'):
            continue

        globals()[name] = value
        __all__.append(name)


@engine.generator("[internal] services list generator.")
def services(stream):
    en_svcs = []
    if(engine.getOption("network", "dnsmasq_enable", toBool)):
        en_svcs.append("dnsmasq")
    if(engine.getOption("network","hostapd_enable", toBool)):
        en_svcs.append("hostapd")

    # get the services which are configured to be turned on.

    services_list = filter(lambda k: k.startswith("service.") and engine.getOption(k, "enabled",toBool) , engine.getSections())

    for s in services_list:
        en_svcs.append( s[s.find(".")+1::] )

    print("SERVICES=( {0} )".format(" ".join(en_svcs)),file=stream)