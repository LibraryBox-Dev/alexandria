Adding a service to Alexandria:

* Add your service to the configuration file: service.foo
* make sure your configuration script is set up: services.d/foo.cfg (make sure it's marked executable!)
* make sure your run script is set up: services.d/foo.run (make sure it's marked executable!)

your .run script will be called from the Alexandria install directory by Supervisor by way of libctl.
your .cfg script will be called from the Alexandria install directory by genconfig.

It is advised that you place configuration files in $AVARDIR 

When running or configuring, the following environment variables will be set:

* AVARDIR: A path to Alexandria's /var/ directory
* ARUNDIR: A path to Alexandria's /run/ directory
* ABINDIR: A path to Alexandria's /bin/ directory
* VENVPY:  Path to the Python3 virtualenv executable

To generate configuration based on Alexandria's config file:

Add a generator to ConfigEngine/Generators (use the dnsmasq one as an example)
and call it.

for example, if you have the service foo and it needs configuration, add foo.py to
ConfigEngine/Generators with the contents

```
from ConfigEngine.Generators import engine

@engine.generator(needs_argument=False)
def fooService(stream):
	print("# my service configuration", file=stream)
	print("MyPath="+engine.getOption("service.foo", "somepath"), file=stream)
```

See the baked in dnsmasq and hostapd configuration generators for more detail.

If you need to expand any environment variables, do so with `envsubst`
from gettext (installed by default) in your configuration, or use Python's system
environment variable tool.

In your scripts, $CFGTOOL is the path and enough boilerplate to call the configuration
generator:

```$CFGTOOL -outfile ${AVARDIR}/hostapd.conf hostapd```


