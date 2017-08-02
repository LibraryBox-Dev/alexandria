. /etc/alexandria-env


TOOL="$VENVPY $ABINDIR/cfgtool.py -baseconfig ${BASECONFIG} -localconfig ${LOCALCONFIG}"

# Now that we've gotten everything configured, we're going to mount

$TOOL -outfile ${ARUNDIR}/mount-env mounts
. ${ARUNDIR}/mount-env

if [ $MODE != "manual" ]; then
    # Check that the mountpoint and the mount device exist
    if [ ! -b $DEVICE ]; then
        exit 1
    fi
    if [ ! -d $MOUNTPOINT  ]; then
        exit 1
    fi
    mount -t auto -o $MOUNTOPTS $DEVICE $MOUNTPOINT
fi
