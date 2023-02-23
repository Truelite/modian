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
