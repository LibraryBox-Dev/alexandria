from ConfigEngine import ConfigEngine, toBool, writeLines

engine = ConfigEngine()

__all__ = []

# This little bit of fancyness lets us add more (and unique!)
# groups to the configuration generators.
import pkgutil
import inspect

for loader, name, is_pkg in pkgutil.walk_packages(__path__):
    module = loader.find_module(name).load_module(name)

    for name, value in inspect.getmembers(module):
        if name.startswith('__'):
            continue

        globals()[name] = value
        __all__.append(name)

def get_enabled_services():
    services = []
    for s in engine.getSections():
        if not s.startswith("service."):
            continue
        elif not engine.getOption(s,"enabled",toBool):
            continue
        sreal = s[s.find('.')+1::]
        services.append(sreal)
    return services

@engine.generator("[internal] services list generator.")
def services(stream):
    print("SERVICES=( {0} )".format(" ".join(get_enabled_services())),file=stream)

@engine.generator("Supervisord configuration generator")
def supervisord_services(stream):
    services = get_enabled_services()
    for service in services:
        print("[program:svc_{0}]".format(service),file=stream)
        print("command=libctl.sh {0}".format(service),file=stream)
        print("",file=stream)
