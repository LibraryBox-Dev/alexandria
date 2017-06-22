#!/bin/bash

. /etc/alexandria-env

function start
{
	# start dnsmasq
	dnsmasq \
		--dhcp-leasefile=${ARUNDIR}/dhcp-leases \
		-C ${AVARDIR}/dnsmasq.conf \
		--pid-file=${ARUNDIR}/dnsmasq.pid \
		& > /dev/null
	# start hostapd
	hostapd \
		-B -P ${ALEXANDRIAPATH}/run/hostapd.pid\
		${ALEXANDRIAPATH}/var/hostapd.conf \
		&>/dev/null
	
	# TODO: Launch any addon services.
}

function stop {
	kill -15 `cat ${ARUNDIR}/dnsmasq.pid` > /dev/null
	kill -15 `cat ${ARUNDIR}/hostapd.pid` > /dev/null
	kill -15 `cat ${ARUNDIR}/libsrv.pid`  > /dev/null
}

function fastcgi
{
	${VENVPY} runserver.py \
		-baseconfig ${BASECONFIG} \
		-localconfig ${LOCALCONFIG} \
		-fastcgi-socket /var/run/lighttpd/alexandria.socket \
		-pidfile /var/run/alexandria-fastcgi.pid
}

case $1 in
	"start")
		start
		exit 0
		;;
	"stop")
		stop
		exit 0
		;;
	"fastcgi")
		fastcgi
		;;
	*)
		echo "Usage: $0 [start|stop|fastcgi]"
		echo "starts or stops library daemons, starts the library fastcgi daemon."
		exit 1
		;;
esac