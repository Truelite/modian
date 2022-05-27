# Library of functions used by modian's first-install procedure
RUN_INFO_FILE=/root/modian-install-result

if efibootmgr > /dev/null 2>&1
then
    IS_UEFI=true
else
    IS_UEFI=false
fi

# Terminal control codes to change text color
COLOR_BLACK=$'\033[0;30m'
COLOR_WHITE=$'\033[1;37m'
COLOR_GREEN=$'\033[0;32m'
COLOR_GREEN_LIGHT=$'\033[1;32m'
COLOR_RED=$'\033[0;31m'
COLOR_RED_LIGHT=$'\033[1;31m'
COLOR_NORMAL=$'\033[0;39m'
COLOR_YELLOW=$'\033[1;33m'
COLOR_BLUE=$'\033[0;34m'
COLOR_BLUE_LIGHT=$'\033[1;34m'
COLOR_CYAN=$'\033[0;36m'
COLOR_CYAN_LIGHT=$'\033[1;36m'
COLOR_GRAY_LIGHT=$'\033[0;37m'
COLOR_GRAY_DARK=$'\033[1;30m'
COLOR_PURPLE=$'\033[0;35m'
COLOR_PURPLE_LIGHT=$'\033[1;35m'
COLOR_BROWN=$'\033[0;33m'

# Systemd log level prefixes
#define SD_EMERG   "<0>"  /* system is unusable */
#define SD_ALERT   "<1>"  /* action must be taken immediately */
#define SD_CRIT    "<2>"  /* critical conditions */
#define SD_ERR	   "<3>"  /* error conditions */
#define SD_WARNING "<4>"  /* warning conditions */
#define SD_NOTICE  "<5>"  /* normal but significant condition */
#define SD_INFO    "<6>"  /* informational */
#define SD_DEBUG   "<7>"  /* debug-level messages */</pre><p>These prefixes are intended to be used in conjunction with

debug() {
    echo "<7>$@" >&2
}
progress() {
    echo "<6>$@" >&2
}
verbose() {
    echo "<5>$@" >&2
}
warning() {
    echo "<4>$@" >&2
}
error() {
    echo "<3>$@" >&2
}
fail()
{
    echo "<2>$@" >&2
    exit 1
}

# Read the config.sh (this should really happen in the python command, however)
. /etc/modian/config.sh

#return the disk size in GiB
#Parameter device name (ex: /dev/sda)
getGiBdisksize()
{
	local size_with_decimal=$(fdisk -l | grep "Disk $1" | awk '{ print $3}')
	#remove decimal
	echo ${size_with_decimal%.*}
}

# Format the given device using the given label
format()
{
    local label="$1"
    local DEVICE="$2"
    progress "$DEVICE: setting up $label partition"
    # If the partition is mounted we try to umount it; if it fails because the
    # partition wasn't mounted it's ok, for any other error mkfs will refuse to
    # work anyway.
    umount $DEVICE || true
    mkfs.ext4 -q -F -L $label $DEVICE
    tune2fs -c 0 -i 1m $DEVICE
}

# Format the images partition
format_part_images()
{
    format '##images##' /dev/$PART_IMAGES
}

#This function returm the partition name
#Param 1: diskname
#Param 2: partition number
getPartitionDiskName() 
{
    local nvmeDisk="nvme"
    local sataDisk="sd"
    local diskName="$1"
    local partitionNumber="$2"	
    if [ -z "${diskName##*$nvmeDisk*}" ] ;then
	#Nel caso di disco nvme devo aggiungere oltre al numero anche la lettera p
	#Esempio nomedisco nvme0n1 --> la partizione 1 diventa --> nvme0n1p1
	echo "${diskName}p${partitionNumber}"
	exit 0
    fi
    if [ -z "${diskName##*$sataDisk*}" ] ;then
	#Nel caso di disco sata sd devo aggiungere solamente il numero
	#Esempio nomedisco sda --> la partizione 1 diventa --> sda1
	echo "${diskName}${partitionNumber}"
	exit 0
    fi
    echo "Error no diskName ${diskName} found"
    exit 1
}

setup_disk_images()
{
    local DISKNAME DEVICE
    DISKNAME="$DISK_IMG"
    if [ -z "$DISK_IMG" ]
    then
        return
    fi
    DEVICE="/dev/${DISK_IMG}"

    progress "$DEVICE: partitioning images disk"
    partition_disk "$DEVICE" datadisk
    PART_IMAGES=$(getPartitionDiskName "${DISKNAME}" "1")
    #PART_IMAGES="${DISKNAME}1"

    # Formattazione 
    format_part_images

}

do_first_install()
{
    return

    # this is ignored, even if it still has to be migrated

    progress "Data partition detection"
    TMPDIR=$(mktemp -d)
    BACKUPDIR=$(mktemp -d)
    for DDISK in $(ls /dev/disk/by-uuid); do
        if mount /dev/disk/by-uuid/${DDISK} ${TMPDIR} &>/dev/null; then
            if [ -d ${TMPDIR}/System ]; then
                cp -a ${TMPDIR}/System ${BACKUPDIR}
                umount ${TMPDIR}
		verbose "System found in ${DDISK}"
	        break
            fi
            umount ${TMPDIR}
        fi
    done

    # Umount all partitions from the target drives
    if [ -n "$DISK_IMG" ]
    then
        for dev in $(grep ^/dev/$DISK_IMG /proc/mounts | sed -re 's/[[:space:]].+//')
        do
            progress "Umounting $dev (on the img disk)"
            umount $dev
        done
    fi
    for dev in $(grep ^/dev/$DISK_ROOT /proc/mounts | sed -re 's/[[:space:]].+//')
    do
        progress "Umounting $dev (on the root disk)"
        umount $dev
    done
    echo ""

    progress "Restore data partition"
    if [ -d ${BACKUPDIR}/System ]; then
        if mount /dev/${PART_DATA} ${TMPDIR} &>/dev/null; then
            cp -a ${BACKUPDIR}/System ${TMPDIR}
            umount ${TMPDIR}
            verbose "System restored in ${PART_DATA}"
        else
            verbose "mount ${PART_DATA} failure"
        fi
    else
        verbose "System dir is not found"
    fi
}

# Print a string centered on the terminal
display_center()
{
    COLOR="$1"
    TEXT="$2"
    printf "%s%*s%s\n" "$COLOR" $(( (${#TEXT} + $COLUMNS) / 2 )) "$TEXT" "$COLOR_NORMAL"
}

# Print empty lines so that $1 lines of text can be printed at the center of
# the screen
vcenter()
{
    for i in $(seq 1 $(( ($LINES - $1) / 2 )))
    do
        echo
    done
}

ruler() {
    echo "$COLOR_YELLOW$RULER$COLOR_NORMAL"
}

beep_ok() {
    while true
    do
        beep -f 500 -l 150
        read -t 1 && break
    done
}

beep_fail() {
    while true
    do
        beep -f 500 -l 150 -d 100 -r 3
        sleep 0.4
        beep -f 500 -l 500 -d 200 -r 3
        sleep 0.2
        beep -f 500 -l 150 -d 100 -r 3
        sleep 0.4
        read -t 1 && break
    done
}

do_feedback_did_not_run() {
    ruler
    vcenter 6
    display_center $COLOR_RED_LIGHT "Installation did not run."
    display_center $COLOR_RED_LIGHT "Check journalctl -u modian-install for more information."
    vcenter 6
    ruler
}

do_feedback_ok() {
    ruler
    vcenter 11

    display_center $COLOR_GREEN_LIGHT "Installation successful ($ACTIONS)."
    display_center $COLOR_GREEN_LIGHT "System disk: $DISK_ROOT ($(cat /sys/block/$DISK_ROOT/device/model))"
    if [ -n "${DISK_IMG}" ]; then
        display_center $COLOR_GREEN_LIGHT "Data disk: $DISK_IMG ($(cat /sys/block/$DISK_IMG/device/model))"
    fi
    display_center $COLOR_GREEN_LIGHT "Please remove the USB key and power cycle into the new system."
    display_center $COLOR_GREEN_LIGHT "Otherwise press ALT+F2 to get a console"
    display_center $COLOR_GREEN_LIGHT ""
    display_center $COLOR_GREEN_LIGHT "You can use 'journalctl -u modian-install' to see the installation output."

    vcenter 11
    ruler

    beep_ok
}

do_feedback_fail()
{
    ruler
    vcenter 10

    display_center $COLOR_RED_LIGHT "Installation failed ($ACTIONS)."
    display_center $COLOR_RED_LIGHT "System disk: $DISK_ROOT ($(cat /sys/block/$DISK_ROOT/device/model))"
    if [ -n "${DISK_IMG}" ]; then
        display_center $COLOR_RED_LIGHT "Data disk: $DISK_IMG ($(cat /sys/block/$DISK_IMG/device/model))"
    fi
    display_center $COLOR_RED_LIGHT "Press ALT+F2 to get a console"
    display_center $COLOR_RED_LIGHT ""
    display_center $COLOR_RED_LIGHT "You can use 'journalctl -u modian-install' to see the installation output."

    vcenter 10
    ruler

    beep_fail
}

do_feedback() {
    LINES=$(tput lines)
    COLUMNS=$(tput cols)
    RULER=$(printf '=%.s' $(seq 1 $COLUMNS))

    if [ ! -e $RUN_INFO_FILE ]
    then
        do_feedback_did_not_run
        beep_fail
    else
        # Read results from last run
        source $RUN_INFO_FILE

        # Beepy feedback
        if [ x"$RESULT" = x"0" ]
        then
            do_feedback_ok
        else
            do_feedback_fail
        fi
    fi
}
