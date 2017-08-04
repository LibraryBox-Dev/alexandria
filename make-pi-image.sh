#!/bin/bash

if [ $# -lt 3 ]; then 
    echo "USAGE: $0 <base> <sourcedir> <outputdir>"
    echo "<base> := a Raspbian (lite) base"
    echo "<sourcedir> := Full path to Alexandria source tree"
    echo "<outputdir> := Full path to output directory"
    exit 1
fi

BASEFILE=$1
SOURCEPATH=$2
OUTDIR=$3

if [ ! -d $SOURCEPATH ]; then
    echo "FAIL: source directory doesn't exist."
    exit 1
fi

if [ ! -d $OUTDIR ]; then
    echo "FAIL: output directory doesn't exist."
    exit 1
fi

if [ ! -f $BASEFILE ]; then
    echo "FAIL: Base image does not exist."
    exit 1
fi


TARGET=${OUTDIR}alexandria-$(date -Iminutes).img

echo "INFO: copy ${BASEFILE} to ${TARGET}"
cp $BASEFILE $TARGET

echo "INFO: Hitch up ${TARGET} on loop7"
losetup -P /dev/loop7 $TARGET

echo "INFO: Mount /dev/loop7p2 as /mnt"
mount /dev/loop7p2 /mnt
echo "INFO: Mount /dev/loop7p1 as /mnt/boot"
mount /dev/loop7p1 /mnt/boot

echo "INFO: Copying source files from ${SOURCEPATH}"
cp -r $SOURCEPATH /mnt/opt/

# Clean up virtualenv stuff
if [ -d /mnt/opt/alexandria/venv ]; then
    echo "WARN: CLeaning virtualenv files up from potential non-native Python installation."
    rm /mnt/opt/alexandria/venv -rf
fi

echo "INFO: Starting systemd-nspawn in qemu-arm-static mode"
systemd-nspawn --bind `which qemu-arm-static` -D /mnt bin/bash /opt/alexandria/install.sh

echo "INFO: Unmounting /mnt/boot and /mnt"
umount /mnt/boot
umount /mnt/
echo "INFO: Disconnecting loopback devices in losetup"
losetup -D 

if [ -f ${OUTDIR}/alexandria-latest.img ]; then
	rm ${OUTDIR}/alexandria-latest.img
fi

echo "INFO: linking ${TARGET} to ${OUTDIR}/alexandria-latest.img"
ln -s $TARGET ${OUTDIR}/alexandria-latest.img

echo "INFO: zipping ${TARGET}"
zip ${TARGET}.zip ${TARGET}

