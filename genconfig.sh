#!/bin/bash

# genconfig: Generate configuration files for the system

. /etc/alexandria-env

TOOL=${VENVPY} ${ABINDIR}/cfgtool.py -baseconfig ${BASECONFIG} -localconfig ${LOCALCONFIG}

# We're going to start by configuring Debian's interface file and getting things
# set up here.

$TOOL -outfile $AVARDIR/interfaces debian_interface:wlan0 debian_interface:eth0 
$TOOL -outfile ${AVARDIR}/dnsmasq.conf dnsmasq
$TOOL -outfile ${AVARDIR}hostapd.conf hostapd