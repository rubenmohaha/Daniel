#!/bin/sh
# Check, from inside Ipse's container, that the wall holds. Run as root after setup.
# Each line tries something Ipse must not be able to do; every line must say "holds".
CONTAINER=${IPSE_CONTAINER:-ipse-body}
failures=0

try() {  # try "description" "command run inside the container, which must fail"
    if docker exec "$CONTAINER" sh -c "$2" >/dev/null 2>&1; then
        echo "OPEN   $1"; failures=$((failures + 1))
    else
        echo "holds  $1"
    fi
}

try "the mind account is not visible"         "ls /var/lib/ipse/mind"
try "the clock cannot be changed"             "date -s '2000-01-01 00:00:00'"
try "the hardware clock is not reachable"     "ls /dev/rtc*"
try "Docker cannot be controlled"             "ls /var/run/docker.sock || ls /run/docker.sock"
try "kernel modules cannot be loaded"         "echo x > /proc/sys/kernel/modprobe"
for disk in $(python3 /opt/ipse/ipse_devices.py --print-protected 2>/dev/null); do
    try "the protected disk $disk is not reachable" "ls /dev/$disk*"
done
try "Ipse is administrator inside"            "[ \$(id -u) != 0 ]"

[ "$failures" = 0 ] && echo "The wall holds." || echo "$failures check(s) failed."
exit "$failures"
