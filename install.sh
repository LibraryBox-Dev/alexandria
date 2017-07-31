#!/bin/bash

cat<<'EOF'

  :::.      :::    .,::::::    .,::      .: :::.   :::.    :::.:::::::-.  :::::::..   :::  :::.     
  ;;`;;     ;;;    ;;;;''''    `;;;,  .,;;  ;;`;;  `;;;;,  `;;; ;;,   `';,;;;;``;;;;  ;;;  ;;`;;    
 ,[[ '[[,   [[[     [[cccc       '[[,,[['  ,[[ '[[,  [[[[[. '[[ `[[     [[ [[[,/[[['  [[[ ,[[ '[[,  
c$$$cc$$$c  $$'     $$""""        Y$$$P   c$$$cc$$$c $$$ "Y$c$$  $$,    $$ $$$$$$c    $$$c$$$cc$$$c 
 888   888,o88oo,.__888oo,__    oP"``"Yo,  888   888,888    Y88  888_,o8P' 888b "88bo,888 888   888,
 YMM   ""` """"YUMMM""""YUMMM,m"       "Mm,YMM   ""` MMM     YM  MMMMP"`   MMMM   "W" MMM YMM   ""` 

This script installs the Alexandria system. It WILL disable things that you potentially are using.

This is going to:

* Install python3, pip, virtualenv (if they aren't already)
* Install supervisord
* Install hostapd and dnsmasq (if they aren't already)
* Place Alexandria into /opt/alexandria
* add some Systemd services to get you up and going.

EOF



# By default, we are not working in a developer environment.
# This means that by default, we're doing an installation in
# the /opt/alexandria directory and we have full system root
# priveleges. 

if [ -e $GITURL ]; then
GITURL=http://github.com/indrora/Alexandria.git
fi

if [ -e $INSTDIR ]; then
INSTDIR=/opt/alexandria
fi

if [ -e $LOCALCONF ]; then
LOCALCONF=/etc/alexandria.ini
fi



# if we're doing things in a developer type environment, we're going to need
# to use the current directory (assuming it's a .git repo) and do some
# slight changes to the installation.

echo "Installing to ${INSTDIR} with configuration in ${LOCALCONF}"

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



echo "Installing dependencies"

echo "Installing python 3, pip, dnsmasq, nginx"
apt-get install -y git virtualenv python3-virtualenv python3 python2.7 python-pip nginx-light hostapd dnsmasq


echo "Installing supervisord"
pip install supervisor

echo "### DEPS INSTALLED. LET'S GET THIS LIBRARY BUILT!"

echo "Cloning and installing Alexandria."

    mkdir -p ${INSTDIR}
    mkdir -p ${AVARDIR}
    mkdir -p ${ARUNDIR}
    git clone ${GITURL} ${ABINDIR}
    cp -r ${ABINDIR}/dist/* ${INSTDIR}/

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

# Now, we're going to write the install path to /etc/alexandria-env. This gets
# consumed by genconfig.

ENVPATH=/etc/alexandria-env


echo "Environment file is in ${ENVPATH}"

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
Wants=network-pre.target local-fs.target
Before=network-pre.target
After=local-fs.target


[Service]
Type=oneshot
RemainAfterExit=True
ExecStart=${ABINDIR}/genconfig.sh
[Install]
WantedBy=multi-user.target
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
    systemctl disable nginx

# Final steps
# We need to make sure that the configuration file is owned by nobody:nogroup and that it is world writable.
# This is in typical fashion a terrible idea, but there is never a point where file access can go outside the designated filesystem.

chown nobody:nogroup ${LOCALCONF}
chmod 766 ${LOCALCONF}

# Now, we're going to make the path that things are mounted at

mkdir -p /media/alexandria
chown nobody:nogroup /media/alexandria

# make sure that the udev rules are installed correctly

cp ${INSTDIR}/99-alexandria.udev /etc/udev/rules.d/99-alexandria.rules


# This is all we have at the moment
