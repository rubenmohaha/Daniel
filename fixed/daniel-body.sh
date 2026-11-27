#!/bin/sh
# Daniel's container. Run as root by the service daniel-body, at each start of
# the robot and again whenever the container stops.
#
# The container is made anew each time, with every device present at that
# moment (see daniel_devices.py): a device connected since the last start is
# handed over, and one that has gone does not prevent the start. What Daniel
# has installed is kept from one container to the next: its folder /self, and
# the folders where a Linux system keeps its software and its settings. The
# container is on the robot's own network.
#
# Daniel is administrator inside, with every device but the excluded ones, and
# no access to the system disk, to the clock or to Docker.
set -eu

CONTAINER=${DANIEL_CONTAINER:-daniel-body}
IMAGE=debian:stable-slim
ROOT=/var/lib/daniel
KEPT="usr var etc opt root home srv"

if [ "${1:-}" = ready ]; then  # used by the service: return once the container answers
    until docker exec "$CONTAINER" true 2>/dev/null; do
        kill -0 "$2" 2>/dev/null || exit 1  # the container could not be started
        sleep 1
    done
    exit 0
fi

case "$(docker container inspect --format '{{.HostConfig.AutoRemove}}' "$CONTAINER" 2>/dev/null || true)" in
    true)   # left behind by an earlier run of this script
        docker rm --force "$CONTAINER" >/dev/null ;;
    false)  # made by an earlier version of the fixed part: what Daniel installed is inside
        echo "the container made by an earlier version is set aside as $CONTAINER-old" >&2
        docker update --restart no "$CONTAINER" >/dev/null
        docker stop "$CONTAINER" >/dev/null
        docker rename "$CONTAINER" "$CONTAINER-old" ;;
esac

# The first process of the container only waits. It ends at once when asked to
# stop, and it collects the processes that Daniel leaves behind. Docker's own
# option for this (--init) cannot be used: it places its program under /usr,
# which is one of the kept folders.
FIRST='trap "exit 0" TERM INT; while :; do sleep 86400 & wait $!; done'

volumes=""
for folder in $KEPT; do
    volumes="$volumes --volume daniel-$folder:/$folder"
done
devices=$(python3 /opt/daniel/daniel_devices.py)

# shellcheck disable=SC2086  # one argument per word, no spaces inside
exec docker run --rm --name "$CONTAINER" --network host \
    --hostname daniel --add-host daniel:127.0.1.1 \
    --volume "$ROOT/self:/self" --workdir /self $volumes $devices \
    "$IMAGE" sh -c "$FIRST"
