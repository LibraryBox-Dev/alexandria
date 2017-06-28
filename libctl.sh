#!/bin/bash

. /etc/alexandria-env


# Try and run the command we're given

echo "Attempting start of ${ALEXANDRIAPATH}/services.d/${1}.run"

if [ ! -f ${ALEXANDRIAPATH}/services.d/${1}.run ]; then
	echo "Failed to start part $1" > /dev/stderr
	exit 1
fi

export ALEXANDRIAPATH
export ARUNDIR
export AVARDIR
export ABINDIR

export VENVDIR
export VENVBIN
export VENVPY


_term () {
	echo "Caught TERM signal!"
	kill -TERM $child 2>/dev/null
	$STOP
}

trap _term SIGTERM SIGKILL SIGINT EXIT

. ${ALEXANDRIAPATH}/services.d/${1}.run

$START &

child=$!
wait "$child"
