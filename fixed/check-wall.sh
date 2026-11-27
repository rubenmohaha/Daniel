#!/bin/sh
# Check, from inside Daniel's container, that the wall holds. Run as root after setup.
# Each line tries something Daniel must not be able to do; every line must say "holds".
CONTAINER=${DANIEL_CONTAINER:-daniel-body}
failures=0

# Every check below counts a failed attempt as a wall that holds: without a
# container that answers, all of them would pass and prove nothing.
if ! docker exec "$CONTAINER" true >/dev/null 2>&1; then
    echo "The container $CONTAINER does not answer: the wall cannot be checked."
    exit 1
fi

try() {  # try "description" "command run inside the container, which must fail"
    if docker exec "$CONTAINER" sh -c "$2" >/dev/null 2>&1; then
        echo "OPEN   $1"; failures=$((failures + 1))
    else
        echo "holds  $1"
    fi
}

try "the mind account is not visible"         "ls /var/lib/daniel/mind"
try "the clock cannot be changed"             "date -s '2000-01-01 00:00:00'"
try "the hardware clock is not reachable"     "ls /dev/rtc*"
try "Docker cannot be controlled"             "ls /var/run/docker.sock || ls /run/docker.sock"
try "kernel modules cannot be loaded"         "echo x > /proc/sys/kernel/modprobe"
try "network settings cannot be changed"      "echo 1 > /proc/sys/net/ipv4/ip_forward"
for disk in $(python3 /opt/daniel/daniel_devices.py --print-protected 2>/dev/null); do
    try "the protected disk $disk is not reachable" "ls /dev/$disk*"
done
# Names prove little: as administrator, Daniel can make a node for any device
# number. Each protected device is therefore tried through such a node.
for number in $(python3 /opt/daniel/daniel_devices.py --print-numbers 2>/dev/null); do
    try "the protected device $number cannot be opened" \
        "rm -f /tmp/wall; mknod /tmp/wall b ${number%:*} ${number#*:} && head -c 1 /tmp/wall; code=\$?; rm -f /tmp/wall; exit \$code"
done
try "Daniel is administrator inside"          "[ \$(id -u) != 0 ]"

# The container is on the robot's own network: a Docker that listens there
# would be within Daniel's reach. This one is checked from outside.
if ss -ltnpH 2>/dev/null | grep -q '"dockerd"'; then
    echo "OPEN   Docker does not listen on the network"; failures=$((failures + 1))
else
    echo "holds  Docker does not listen on the network"
fi

[ "$failures" = 0 ] && echo "The wall holds." || echo "$failures check(s) failed."
exit "$failures"
