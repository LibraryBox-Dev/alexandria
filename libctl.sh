#!/bin/bash

. /etc/alexandria-env

start()
{
	# start dnsmasq
	dnsmasq \
		-l ${ALEXANDRIAPATH}/run/dhcp-leases \
		-c ${ALEXANDRIAPATH}/var/dnsmasq.conf \
		-x ${ALEXANDRIAPATH}/run/dnsmasq.pid \
		& > /dev/null
	# start hostapd
	hostapd \
		-P ${ALEXANDRIAPATH}/run/hostapd.pid\
		${ALEXANDRIAPATH}/var/hostapd.conf \
		&>/dev/null
	${VENV}/bin/python3 runserver.py \
		-baseconfig ${ALEXANDRIAPATH}/default.ini  \
		-localconfig ${LOCALCONFIG}  \
		-port 8888  \ 
		-pidfile ${ALEXANDRIAPATH}/run/libsrv.pid
	nohup
}

stop() {
	killall -15 `cat ${ALEXANDRIAPATH}/run/dnsmasq.pid` > /dev/null
	killall -15 `cat ${ALEXANDRIAPATH}/run/hostapd.pid` > /dev/null
	killall -15 `cat ${ALEXANDRIAPATH/run/libsrv.pid`   > /dev/null
}


case @ $1 in
	"start")
		start()
		exit 0
		;;
	"stop")
		stop()
		exit 0
		;;
	*)
		echo "Usage: $0 [start|stop]"
		exit 0
		;;
esac