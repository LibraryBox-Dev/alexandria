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
	${VENVPY} runserver.py \
		-baseconfig ${ALEXANDRIAPATH}/default.ini  \
		-localconfig ${LOCALCONFIG}  \
		-port 8888  \
		-host 0.0.0.0 \
		-pidfile ${ALEXANDRIAPATH}/run/libsrv.pid
}

function stop {
	killall -15 `cat ${ARUNDIR}/dnsmasq.pid` > /dev/null
	killall -15 `cat ${ARUNDIR}/hostapd.pid` > /dev/null
	killall -15 `cat ${ARUNDIR}/libsrv.pid`  > /dev/null
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
	*)
		echo "Usage: $0 [start|stop]"
		exit 0
		;;
esac