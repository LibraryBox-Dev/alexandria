#!/bin/bash


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

virtualenv -p python3 ${INSTDIR}/env

$VENVPIP install -r ${ABINDIR}/requirements.txt

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
echo "ALEXANDRIAPATH=${INSTDIR}">/etc/alexandria-env
echo "LOCALCONFIG=${LOCALCONF}">>/etc/alexandria-env
echo "VENV=${VENVDIR}"


# Now, we need to run the configuration generator script.

${ABINDIR}/genconfig.sh

# We now need to make sure that the systemd configuration is correct. 
# This means we need to generate systemd unit files. 

# This makes sure that the configuration files are written just after we have
# gotten everything stable but the network devices have not been touched yet
# 
# see also https://www.freedesktop.org/wiki/Software/systemd/NetworkTarget/
#
cat<<<EOF>${INSTDIR}/alexandria-config.service
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

cat<<<EOF>${INSTDIR}/alexandria-server.service
[Unit]
Description=Alexandria librarian daemons
after=network.target

[Service]
Type=oneshot
ExecStart=${ABINDIR}/libctl.sh start
ExecStop=${ABINDIR}/libctl.sh stop
EOF

# Now we link them in the right way

ln -s ${INSTDIR}/alexandria-server.service /etc/systemd/system/alexandria-server.service
ln -s ${INSTDIR}/alexandria-config.service /etc/systemd/system/alexandria-config.service

# Now, configure systemd to load them
systemctl daemon-reload
systemctl enable alexandria-config
systemctl enable alexandria-server

# ensure that hostapd and dnsmasq are disabled

echo "Turning off distribution hostapd and dnsmasq"
systemctl disable hostapd
systemctl disable dnsmasq

# This is all we have at the moment