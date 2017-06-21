#!/bin/bash

if [ $(whoami) != "root" ]; then
	echo "I need to be run as root!"
	exit 1
fi

if [ -e $GITURL ]; then
GITURL=http://github.com/indrora/Alexandria.git
fi

if [ -e $INSTDIR ]; then
INSTDIR=/opt/alexandria
fi

if [ -e $LOCALCONF ]; then
LOCALCONF=/etc/alexandria.ini
fi

ABINDIR=${INSTDIR}/bin
AVARDIR=${INSTDIR}/var
ARUNDIR=${INSTDIR}/run

VENVDIR=${INSTDIR}/env
VENVBIN=${VENVDIR}/bin
VENVPIP=${VENVBIN}/pip
VENVPY=${VENVBIN}/python

echo "Installing dependencies"

apt-get install -y python3 python3-virtualenv hostapd dnsmasq lighttpd

echo "Cloning and installing Alexandria."

mkdir -p ${INSTDIR}
mkdir -p ${AVARDIR}
mkdir -p ${ARUNDIR}

git clone ${GITURL} ${ABINDIR}

# Now, we're going to make sure that the virtualenv gets what it needs.

virtualenv -p python3 ${INSTDIR}/env > /dev/null

$VENVPIP install -r ${ABINDIR}/requirements.txt > /dev/null

# We now need to generate the configuration 

# To do this, we're going to make sure that the local configuration is placed
# in the right place. By default, this should be an empty file.
#
# The default configuration needs to be in $INSTDIR/alexandria.ini
# The local configuration is, by default, in /etc/alexandria.ini

touch $LOCALCONF
cp ${ABINDIR}/default.ini ${INSTDIR}/alexandria.ini

# Now, we're going to write the install path to /etc/alexandria-env. This gets
# consumed by genconfig.
cat<<EOE>/etc/alexandria-env
ALEXANDRIAPATH=${INSTDIR}
BASECONFIG=${INSTDIR}/alexandria.ini
LOCALCONFIG=${LOCALCONF}

ABINDIR=${INSTDIR}/bin
AVARDIR=${INSTDIR}/var
ARUNDIR=${INSTDIR}/run

VENVDIR=${INSTDIR}/env
VENVBIN=${VENVDIR}/bin
VENVPIP=${VENVBIN}/pip
VENVPY=${VENVBIN}/python

EOE

# we need to set the file mode of our configuration tools

echo "Setting executable bits where needed."

chmod a+x ${ABINDIR}/genconfig.sh
chmod a+x ${ABINDIR}/libctl.sh

# By only using these as executables (and thin ones at that) the security risk is lessened.

# Now, we need to run the configuration generator script.

echo "Backing up /etc/network/interfaces"
cp /etc/network/interfaces /etc/network/interfaces.dist

echo "Running configuration"
${ABINDIR}/genconfig.sh

# We now need to make sure that the systemd configuration is correct. 
# This means we need to generate systemd unit files. 

# This makes sure that the configuration files are written just after we have
# gotten everything stable but the network devices have not been touched yet
# 
# see also https://www.freedesktop.org/wiki/Software/systemd/NetworkTarget/
#
echo "Writing systemd units"

cat<<EOF>${INSTDIR}/alexandria-config.service
[Unit]
Description=Alexandria configuration
DefaultDependencies=no
Before=network-pre.target
Wants=network-pre.target
[Service]
type=oneshot
RemainAfterExit=True
ExecStart=${ABINDIR}/genconfig.sh
[Install]
WantedBy=multi-user.target
EOF

cat<<EOF>${INSTDIR}/alexandria-server.service
[Unit]
Description=Alexandria librarian daemons
after=network.target

[Service]
Type=oneshot
ExecStart=${ABINDIR}/libctl.sh start
ExecStop=${ABINDIR}/libctl.sh stop
EOF

# Now we link them in the right way

echo "Enabling systemd units"
# By doing this, we usurp the need to add them. However, disabling them will
# cause them to go away (this is why we symlinked!)
ln -s ${INSTDIR}/alexandria-server.service /etc/systemd/system/alexandria-server.service
ln -s ${INSTDIR}/alexandria-config.service /etc/systemd/system/alexandria-config.service

echo "Reloading systemd's unit configuration"
# Now, configure systemd to load them
systemctl daemon-reload

# ensure that hostapd and dnsmasq are disabled

echo "Turning off distribution hostapd and dnsmasq"
systemctl disable hostapd
systemctl disable dnsmasq

# This is all we have at the moment