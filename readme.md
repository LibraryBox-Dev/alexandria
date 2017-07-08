
      :::.      :::    .,::::::    .,::      .: :::.   :::.    :::.:::::::-.  :::::::..   :::  :::.     
      ;;`;;     ;;;    ;;;;''''    `;;;,  .,;;  ;;`;;  `;;;;,  `;;; ;;,   `';,;;;;``;;;;  ;;;  ;;`;;    
     ,[[ '[[,   [[[     [[cccc       '[[,,[['  ,[[ '[[,  [[[[[. '[[ `[[     [[ [[[,/[[['  [[[ ,[[ '[[,  
    c$$$cc$$$c  $$'     $$""""        Y$$$P   c$$$cc$$$c $$$ "Y$c$$  $$,    $$ $$$$$$c    $$$c$$$cc$$$c 
     888   888,o88oo,.__888oo,__    oP"``"Yo,  888   888,888    Y88  888_,o8P' 888b "88bo,888 888   888,
     YMM   ""` """"YUMMM""""YUMMM,m"       "Mm,YMM   ""` MMM     YM  MMMMP"`   MMMM   "W" MMM YMM   ""` 

# Introduction
Alexandria is a librarian for files, intended to replace the scripts that run LibraryBox and PirateBox

Alexandria has two parts: The library server and the configuration generator.

The library server has two functions:

  * browsing and management of files
  * Configuration of the overall system

The configuration generator... generates configuration files!

# Architecture

Here you'll find we refer to two files: the Base config and the Local config. The base config is a file
that holds all the default options. Any option which can be set should have its sensible default set here,
even if that value is an empty one.

Let's consider the following "base" config:

```
[general]
some_option=five
another_option=potato
```

If the local configuration has the following contents:

```
[general]
some_option=six
```

then the value in the base configuration is overruled by the local configuration.

An empty local configuration is always valid, but an empty base configuration is not.



## LibServ

LibServ is the actual librarian service. It has two roles:

    * Browsing and management of files
    * Administration

LibServ consumes the configuration at start-time. The values are not at regular intervals re-read, and
any change to the settings that affect the operation of LibServ will only take effect after LibServ is
restarted.

## genconfig

`genconfig` exists to generate configurations from the base and local configurations. It relies heavily
on a python script, cfgtool

## cfgtool

`cfgtool` is the primary mode of interaction with ConfigEngine, the configuration generator engine.

## ConfigEngine

ConfigEngine is the configuration file generation engine. It operates by taking the local and base
configuration files, merging them, then allowing the various configuration outputs ('generators') to
read the configuration file, assert the presence of certain options, as well as potentially combine
other generators. For instance, a simple generator can be as easy as

```
@engine.generator('Configure the debian Loopback interface')
def debian_loopback(outstream):
    print("auto lo","iface lo inet loopback", file=outstream)
```

while more complex generators might call `engine.getSection(section)`. See `ConfigEngine.Generators.network`
for more examples of generators.

Adding a generator simply requires adding a python module to `ConfigEngine.Generators` and adding the
`@engine.generator(desc)` decorator as the final decorator.

# Services that Alexandria's configuration interface can handle

By default, Alexandria has some built-in configuration systems. It assumes a Debian-like system below, however
this can be easily changed.

Included services are:

* hostapd (802.11 AP host)
* dnsmasq (DNS and DHCP)
* btle-beacon (Bluetooth beaconing)


#Running Alexandria's Librarian only

Alexandria can be happily run with only the librarian running. To do so, simply pass the -no-admin option to
runserver.py. Check the output of runserver.py -h

It is possible to only have the LibServer portion of Alexandria and set up the flask environment manually.
Look at runserver.py to see how this can be done.

Alexandria's parts are as follows:

genconfig.sh        generates system-wide configuration.
libctl.sh           is responsible for running daemons and other parts.

Alexandria was intended to be run on top of Supervisor, such that the following process hierarchy is
achieved:

* supervisord
`-libctl httpd---nginx
`-libctl libsrv--runserver
`-libctl dnsmasq-dnsmasq
`-libctl hostapd-hostapd
`-libctl [...]---SOME_DAEMON

# Adding services to Alexandria

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

