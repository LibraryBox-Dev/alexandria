#!/bin/bash

# genconfig: Generate configuration files for the system

. /etc/alexandria-env

TOOL="$VENVPY $ABINDIR/cfgtool.py -baseconfig ${BASECONFIG} -localconfig ${LOCALCONFIG}"

# We're going to start by configuring Debian's interface file and getting things
# set up here.

export CFGTOOL=$TOOL
export AVARDIR
export ABINDIR
export ARUNDIR
export ALEXANDRIAPATH
export VENVPY

# We need to generate the config for supervisor here.

# To do that, we need to generate the configuration for services.

$TOOL -outfile ${ARUNDIR}/services

. ${ARUNDIR}/services

#$TOOL -outfile /etc/network/interfaces \
#	debian_loopback \
#	debian_interface:wlan0 \
#	debian_interface:eth0 
$TOOL -outfile ${AVARDIR}/dnsmasq.conf dnsmasq
$TOOL -outfile ${AVARDIR}/hostapd.conf hostapd

# later: $AVARDIR/conf.d will contain some things we care about. 
# These include things that may have been generated by another page here.

for service in $SERVICES; do
	if [ -f ${ALEXANDRIAPATH}/services.d/${service}.cfg ]; then
		# try to run it.
		${ALEXANDRIAPATH}/services.d/${service}.cfg || echo "Failed to run configuration script for ${service}">/dev/stderr
	fi
done



# End genconfig5
