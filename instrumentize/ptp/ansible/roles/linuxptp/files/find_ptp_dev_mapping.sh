#!/bin/bash

MASTER_IFACE_NAME=''
ALL_NICS=0
function show_help {
    echo "Usage: ${0} -m [Managament Interface Name] -[1|0]]"
    echo ""
    echo "    -m: Management Interface Name"
    echo "    -a: Synchronize all Available PTP Clocks (1 for Yes or 0 for No)"
    exit 0
}
# A POSIX variable

OPTIND=1 # Reset in case getopts has been used previously in the shell.
# set -x

while getopts ":hm:a:" opt; do
	case "$opt" in
    m) 
		MASTER_IFACE_NAME=${OPTARG}
		;;
	a)
        	ALL_NICS=${OPTARG} 
		;;
	h|\?)
        	show_help
	    	exit 0
        	;;
    esac
done

is_KVM=`systemd-detect-virt`
if [[ $is_KVM != 'kvm' ]]; then
	mkdir -p /etc/linuxptp/conf.d
	PTP4L_CONF_TAIL="/etc/linuxptp/conf.d/ptp4l.conf.tail"
	touch $PTP4L_CONF_TAIL
	truncate -s0 $PTP4L_CONF_TAIL
fi
IFACES=`find /sys/class/net -type l -not -lname '*virtual*' -printf '%f\n'`
for ETHA in $(find /sys/class/net -type l -not -lname '*virtual*' -printf '%f\n')
do
	if [[ $ETHA == $MASTER_IFACE_NAME ]]; then
		continue
	fi
	DEVINDEX=$(ethtool -T $ETHA | awk '/PTP/ {print $4}')
	if [[ $DEVINDEX != 'none' ]] ; then 
		DEVA=/dev/ptp$DEVINDEX
		if [[ $is_KVM == 'kvm' ]]; then
			printf '%s\n' "$ETHA"
		elif [[ $ALL_NICS == 1 ]]; then
			echo "[$ETHA]" >>$PTP4L_CONF_TAIL
			echo "boundary_clock_jbod     1">>$PTP4L_CONF_TAIL
			echo " ">>$PTP4L_CONF_TAIL
		fi
	fi
done
