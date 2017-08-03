#!/bin/bash

cat<<'EOF'
  N E X T  G E N E R A T I O N  O F  H Y P E R L O C A L  F I L E  S H A R I N G -------------------
  :::.      :::    .,::::::    .,::      .: :::.   :::.    :::.:::::::-.  :::::::..   :::  :::.     
  ;;`;;     ;;;    ;;;;''''    `;;;,  .,;;  ;;`;;  `;;;;,  `;;; ;;,   `';,;;;;``;;;;  ;;;  ;;`;;    
 ,[[ '[[,   [[[     [[cccc       '[[,,[['  ,[[ '[[,  [[[[[. '[[ `[[     [[ [[[,/[[['  [[[ ,[[ '[[,  
c$$$cc$$$c  $$'     $$""""        Y$$$P   c$$$cc$$$c $$$ "Y$c$$  $$,    $$ $$$$$$c    $$$c$$$cc$$$c 
 888   888,o88oo,.__888oo,__    oP"``"Yo,  888   888,888    Y88  888_,o8P' 888b "88bo,888 888   888,
 YMM   ""` """"YUMMM""""YUMMM,m"       "Mm,YMM   ""` MMM     YM  MMMMP"`   MMMM   "W" MMM YMM   ""` 
 --------------------------------- B U I L D  T H E  B E S T  L I B R A R Y  T H A T  E V E R  W A S

EOF


if [ -e $INSTDIR ]; then
INSTDIR=$(dirname $(readlink -f $0))
fi

if [ -e $LOCALCONF ]; then
LOCALCONF=/etc/alexandria.ini
fi


echo "install: install dir = ${INSTDIR}"
echo "install: config file = ${LOCALCONF}"

ABINDIR=${INSTDIR}/bin
AVARDIR=${INSTDIR}/var
ARUNDIR=${INSTDIR}/run
VENVDIR=${INSTDIR}/env
VENVBIN=${VENVDIR}/bin
VENVPIP=${VENVBIN}/pip
VENVPY=${VENVBIN}/python


if [ $(whoami) != "root" ]; then
    echo "I need to be run as root!"
    exit 1
fi



echo "install: deps"
echo "install: make sure apt is up to date"
apt-get update
echo "install: apt-get -> python3, virtualenv, nginx-light, hostapd, dnsmasq, nyancat, exfat"
apt-get install -y virtualenv python3-virtualenv python3 python2.7 python-pip nginx-light hostapd dnsmasq nyancat exfat-utils exfat-fuse

echo "install: global pip install of supervisor"
pip install supervisor



# I don't trust that things were brought over with the copy. Let's make sure things that should be there are.
echo "install: enforce install of current filesystem tree"

mkdir -p ${AVARDIR}
mkdir -p ${ARUNDIR}
chown nobody:nogroup ${ARUNDIR}
# We don't put anything sensitive here, so this is mostly safe?
chmod a+rw ${ARUNDIR}

# Now, we're going to make sure that the virtualenv gets what it needs.
echo "venv: create virtualenv python3 at ${VENVDIR}"
virtualenv -p python3 ${VENVDIR} > /dev/null
echo "venv: pip install requirements"
# This was a pain to track down.
$VENVPIP install -r ${INSTDIR}/requirements.txt

echo "install: make sure ${LOCALCONF} exists"
touch $LOCALCONF

# Now, we're going to write the install path to /etc/alexandria-env. This gets
# consumed by genconfig.

ENVPATH=/etc/alexandria-env

echo "install: write environment file at ${ENVPATH}"

cat<<EOE>$ENVPATH
ALEXANDRIAPATH=${INSTDIR}
BASECONFIG=${INSTDIR}/alexandria.ini
LOCALCONFIG=${LOCALCONF}

ABINDIR=${ABINDIR}
AVARDIR=${AVARDIR}
ARUNDIR=${INSTDIR}/run

VENVDIR=${VENVDIR}
VENVBIN=${VENVDIR}/bin
VENVPIP=${VENVBIN}/pip
VENVPY=${VENVBIN}/python

EOE

echo "install: contents of environment file are"
echo ""
cat ${ENVPATH}
echo ""


# we need to set the file mode of our configuration tools

echo "install: enforce execute permissions on scripts"

chmod a+x ${ABINDIR}/genconfig.sh
chmod a+x ${ABINDIR}/libctl.sh

# Tinetd is a super stupid TCP daemon that I wrote.
chmod a+x ${ABINDIR}/tinetd

echo "config: back up current configuration file"
cp /etc/network/interfaces /etc/network/interfaces.dist
echo "config: run initial configuration."
${ABINDIR}/genconfig.sh

# We now need to make sure that the systemd configuration is correct. 
# This means we need to generate systemd unit files. 

# This makes sure that the configuration files are written just after we have
# gotten everything stable but the network devices have not been touched yet
# 
# see also https://www.freedesktop.org/wiki/Software/systemd/NetworkTarget/
#

echo "systemd: start"
echo "systemd: write local copy of unit files."

cat<<EOF>${INSTDIR}/alexandria-config.service
[Unit]
Description=Alexandria configuration
DefaultDependencies=no
Wants=local-fs.target
Before=network-pre.target multi-user.target
After=local-fs.target

[Service]
Type=oneshot
RemainAfterExit=True
ExecStart=${ABINDIR}/genconfig.sh

[Install]
WantedBy=multi-user.target network-pre.target
EOF

cat<<EOF>${INSTDIR}/alexandria-server.service
[Unit]
Description=Alexandria librarian daemons
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/supervisord -c supervisord.conf
WorkingDirectory=${INSTDIR}
Environment="PATH=${ABINDIR}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
EnvironmentFile=/etc/alexandria-env

[Install]
WantedBy=multi-user.target
EOF

# Now we link them in the right way


echo "Systemd: hard link in our service files and get going."
ln ${INSTDIR}/alexandria-server.service /lib/systemd/system/alexandria-server.service
ln ${INSTDIR}/alexandria-config.service /lib/systemd/system/alexandria-config.service

    # ensure that hostapd and dnsmasq are disabled

echo "systemd: disable distribution installed hostapd, dnsmasq and nginx"
systemctl disable hostapd
systemctl disable dnsmasq
systemctl disable nginx

echo "systemd: enable alexandria services."
systemctl enable alexandria-config
systemctl enable alexandria-server

# Final steps
# We need to make sure that the configuration file is owned by nobody:nogroup and that it is world writable.
# This is in typical fashion a terrible idea, but there is never a point where file access can go outside the designated filesystem.

echo "install: set permissions."


echo "install: set permissions permissive on ${LOCALCONF}"
chown nobody:nogroup ${LOCALCONF}
chmod 766 ${LOCALCONF}

# Now, we're going to make the path that things are mounted at
echo "install: add default media path, make it owned by nobody"
mkdir -p /media/alexandria
chown nobody:nogroup /media/alexandria

# make sure that the udev rules are installed correctly
echo "udev: add usbstor rule"
cp ${INSTDIR}/system/udev.rules /etc/udev/rules.d/99-alexandria.rules


# This is all we have at the moment

exit 0
