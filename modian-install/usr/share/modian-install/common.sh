# Library of functions used by modian's first-install procedure
RUN_INFO_FILE=/root/modian-install-result

if efibootmgr > /dev/null 2>&1
then
    IS_UEFI=true
else
    IS_UEFI=false
fi

# look for a custom installation script, or fall back to the default one
if [ -x /etc/modian/install.py ]
then
    INST_SCRIPT=/etc/modian/install.py
elif [ -x /etc/modian/install ]
    INST_SCRIPT=/etc/modian/install
else
    INST_SCRIPT=/usr/sbin/modian_setup.py

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

#return the disk size in GiB
#Parameter device name (ex: /dev/sda)
getGiBdisksize()
{
	local size_with_decimal=$(fdisk -l | grep "Disk $1" | awk '{ print $3}')
	#remove decimal
	echo ${size_with_decimal%.*}
}

# Partition a disk given its device and the name of the parted recipe
# Example: partition_disk /dev/sda ssd
partition_disk()
{
    DEVICE="$1"
    RECIPE="$2"

    # cancellazione MBR
    sgdisk --zap-all "$DEVICE"
    dd if=/dev/zero of="$DEVICE" bs=446 count=1 status=none
    
    local disksizeGiB=$(getGiBdisksize "$DEVICE")
    local partitionTableRecipe=${DATADIR}/${RECIPE}.parted
    if (( $disksizeGiB < 32 )); then
	#disk size < 32GiB, use small partition table 
	partitionTableRecipe=${DATADIR}/${RECIPE}-32G.parted
    fi	    
    # partizionamento
    progress "Partitioning disk ${DEVICE}"
    while read -r cmd; do parted -s -a optimal "$DEVICE" -- $cmd; done < $partitionTableRecipe

    partx -u "$DEVICE"
    partx -s "$DEVICE"
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

# Format the root partition
format_part_root()
{
    format '##root##' /dev/$PART_ROOT
    if [ $IS_UEFI != true ]
    then
        # Install grub and initial system disk structure,
        progress "Installing GRUB"
        mount /dev/$PART_ROOT /mnt
        # Legacy system
        grub-install --no-floppy --root-directory=/mnt /dev/$DISK_ROOT
	install -m 0644 /usr/share/grub/unicode.pf2 /mnt/boot/grub
        modian-install-iso --live-dir=/mnt --no-check-integrity $MODIAN_RELEASE_NAME --isoimage /dev/$DISK_INST --max-installed-versions=$MAX_INSTALLED_VERSIONS
        umount /mnt
    fi
}

# Format the ESP partition
format_part_esp()
{
    local DEVICE="$PART_ESP"
    progress "$DEVICE: setting up ESP partition"
    mkfs.vfat /dev/$DEVICE
    if [ $IS_UEFI = true ]
    then
        # Install grub and initial system disk structure,
        progress "Installing GRUB"
        mount /dev/$PART_ROOT /mnt
        # UEFI system

        # Mount ESP partition
        mkdir -p /boot/efi
        mount /dev/$PART_ESP /boot/efi
        grub-install --no-floppy --efi-directory=/boot/efi --root-directory=/mnt /dev/$DISK_ROOT
        install -m 0644 /usr/share/grub/unicode.pf2 /mnt/boot/grub
        modian-install-iso --live-dir=/mnt --no-check-integrity $MODIAN_RELEASE_NAME --isoimage /dev/$DISK_INST --max-installed-versions=$MAX_INSTALLED_VERSIONS
        umount /boot/efi
	umount /mnt
    fi
}

# Format the log partition
format_part_log()
{
    format '##log##' /dev/$PART_LOG
}

# Format the data partition
format_part_data()
{
    local DEVICE=/dev/$PART_DATA
    format '##data##' $DEVICE

    # Create initial directory structure
    mount $DEVICE /mnt
    mkdir -p /mnt/images/inkjet
    mkdir -p /mnt/cfast
    umount /mnt
}

# Format the images partition
format_part_images()
{
    format '##images##' /dev/$PART_IMAGES
}

# Clean lvm groups
clean_lvm_groups()
{
    for lv in $(lvs --noheadings -o lvname)
    do
        verbose "removing ${lv} logical volume"
        lvremove -f ${lv}
    done
    for vg in $(vgs --noheadings -o vgname)
    do
        verbose "removing ${vg} logical volume"
        vgremove -f ${vg}
    done
    for pv in $(pvs --noheadings -o pvname)
    do
        verbose "removing ${pv} phisical volume"
        pvremove -f ${pv}
    done
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

# Setup partitions on the SSD
setup_disk_root()
{
    local DISKNAME DEVICE
    DISKNAME="$DISK_ROOT"
    DEVICE="/dev/${DISK_ROOT}"

    progress "$DEVICE: partitioning root disk"
    if [ $IS_UEFI = true ]
    then
        partition_disk "$DEVICE" systemdisk-uefi
    else
        partition_disk "$DEVICE" systemdisk-bios
    fi
    PART_ROOT=$(getPartitionDiskName "${DISKNAME}" "1")
    #PART_ROOT=${DISKNAME}1
    PART_LOG=$(getPartitionDiskName "${DISKNAME}" "2")
    #PART_LOG=${DISKNAME}2
    PART_DATA=$(getPartitionDiskName "${DISKNAME}" "3")
    #PART_DATA=${DISKNAME}3
    PART_ESP=$(getPartitionDiskName "${DISKNAME}" "4")
    #PART_ESP=${DISKNAME}4

    # Formattazione 
    format_part_root
    format_part_log
    format_part_data
    if [ $IS_UEFI = true ]
    then
        format_part_esp
    fi
}

setup_disk_images()
{
    local DISKNAME DEVICE
    DISKNAME="$DISK_IMG"
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
    # run python installer script first
    $INST_SCRIPT

    # and then do the preexisting script, to do anything that had been missed.
    progress "Disk and partition detection"
    TMPFILE=$(mktemp)
    if [ $IS_UEFI = true ]
    then
	modian-install-detect --uefi --debug > $TMPFILE
    else
	modian-install-detect --debug > $TMPFILE
    fi
    cat $TMPFILE >> $RUN_INFO_FILE
    source $TMPFILE
    rm $TMPFILE
    verbose "Detected system disk: $DISK_ROOT ($(cat /sys/block/$DISK_ROOT/device/model))"
    if [ -n "${DISK_IMG}" ]; then
        verbose "Detected data disk: $DISK_IMG ($(cat /sys/block/$DISK_IMG/device/model))"
    fi
    verbose "Detected uSB disk: $DISK_INST ($(cat /sys/block/$DISK_INST/device/model))"
    verbose "Detected root partition: ${PART_ROOT:-none}"
    verbose "Detected log partition: ${PART_LOG:-none}"
    verbose "Detected data partition: ${PART_DATA:-none}"
    verbose "Detected images partition: ${PART_IMAGES:-none}"
    verbose "Detected first install actions: $ACTIONS"

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

    # tune2fs wants /etc/mtaFirst install a in order to run: creating it if it is missing
    progress "Creating mtab"
    test -e /etc/mtab || ln -s /proc/mounts /etc/mtab

    # In case booting detected a swap partition and enabled it, disable all swap now so hard disks are not used anymore
    progress "Disabling swap"
    swapoff -a

    # Umount all partitions from the target drive
    for dev in $(grep ^$DISK_INST /proc/mounts | sed -re 's/[[:space:]].+//')
    do
	progress "Umounting $dev"
	umount $dev
    done
    echo ""

    progress "performing partitioning and file system creation"
    for a in $ACTIONS
    do
	$a
    done

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
        if [ $RESULT = 0 ]
        then
            do_feedback_ok
        else
            do_feedback_fail
        fi
    fi
}
