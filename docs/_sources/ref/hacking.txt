Hacking on Alexandria
*********************

Alexandria was built to be as extensible as possible. There are a handful of things that are needed to add
something to the interface. 


Services
========

A service under Alexandria must have thee things:

* An entry in either the base or local configuration file, designated as
  - a section named service.<name>
* an executable file in services.d called `<name>.cfg`
* A file in services.d called `<name.run>` containing:
  - A line in the form `START="...."`
  - A line in the form `STOP="...."`

The `.run` file specifies the command to run. It must:

* not be a shell file
* must not fork
* must not spawn subshells

(this may change in the future)

Service configuraition is done by calling `services.d/<name>.cfg`; this will be done from the
alexandria installation directory. 

You will need to add a section to either the local or base configuration (if you are building your own distribution,
you should be adding it to the global configuration). Adding a control panel is as simple as adding a template. Follow the pattern
found in the existing templates, then making sure you have it categorized correctly.


Tool Reference
==============


LibServ
-------

LibServ is the actual librarian service. It has two roles:

    * Browsing and management of files
    * Administration

LibServ consumes the configuration at start-time. The values are not at regular intervals re-read, and
any change to the settings that affect the operation of LibServ will only take effect after LibServ is
restarted.

genconfig
---------

`genconfig` exists to generate configurations from the base and local configurations. It relies heavily
on a python script, cfgtool

cfgtool
-------

`cfgtool` is the primary mode of interaction with ConfigEngine, the configuration generator engine. It is
the means to generate configuration from the generators in ConfigEngine

ConfigEngine
------------

ConfigEngine is the configuration file generation engine. It operates by taking the local and base
configuration files, merging them, then allowing the various configuration outputs ('generators') to
read the configuration file, assert the presence of certain options, as well as potentially combine
other generators. For instance, a simple generator can be as easy as


    @engine.generator('Configure the debian Loopback interface')
    def debian_loopback(outstream):
        print("auto lo","iface lo inet loopback", file=outstream)

while more complex generators might call `engine.getSection(section)`. See `ConfigEngine.Generators.network`
for more examples of generators.

Adding a generator simply requires adding a python module to `ConfigEngine.Generators` and adding the
`@engine.generator(desc)` decorator as the final decorator.

Services that Alexandria's configuration interface can handle
=============================================================

By default, Alexandria has some built-in configuration systems. It assumes a Debian-like system below, however
this can be easily changed.

Included services are:

* hostapd (802.11 AP host)
* dnsmasq (DNS and DHCP)
* btle-beacon (Bluetooth beaconing)

