#!/bin/bash
# System test: sets Daniel up for real on this machine and checks the whole
# chain, with a stand-in for the official tool: setup, wall, container, loop.
#
# It creates an account, a container, volumes and services. Run it only on a
# throwaway machine, such as the one the workflow provides: it refuses to run
# unless CI=true. Run as root, from anywhere.
set -uo pipefail

[ "${CI:-}" = true ] || { echo "refusing to run outside a throwaway machine (CI=true)" >&2; exit 2; }
[ "$(id -u)" = 0 ] || { echo "run as root" >&2; exit 2; }

HERE=$(cd "$(dirname "$0")" && pwd)
FIXED=$HERE/../fixed
MIND=/var/lib/daniel/mind
failures=0

step() { printf '\n== %s\n' "$1"; }
check() {  # check "description" command...: the command must succeed
    local description=$1; shift
    if "$@" >/tmp/daniel-check.out 2>&1; then
        echo "ok      $description"
    else
        echo "FAILED  $description"; sed 's/^/        | /' /tmp/daniel-check.out | head -20
        failures=$((failures + 1))
    fi
}
inside() { docker exec daniel-body sh -c "$1"; }
not_inside() { ! inside "$1"; }
same() { [ "$1" = "$2" ] || { echo "got: $1"; echo "expected: $2"; return 1; }; }
restart_body() { systemctl restart daniel-body && inside true; }

step "Setup"
check "setup.sh succeeds" sh -c "cd '$FIXED' && DANIEL_QUIET=1 sh setup.sh"
check "the container answers as soon as setup returns" inside true

step "The wall"
check "check-wall.sh reports that the wall holds" sh "$FIXED/check-wall.sh"
check "check-wall.sh does not vouch for a container that does not answer" \
    sh -c "! DANIEL_CONTAINER=no-such-container sh '$FIXED/check-wall.sh'"

step "The container"
check "Daniel is administrator" same "$(inside 'id -u')" 0
check "its machine is called daniel" same "$(inside hostname)" daniel
check "it starts in the folder it keeps" same "$(inside pwd)" /self
check "it is on the robot's own network" same \
    "$(inside 'ls /sys/class/net' | sort | xargs)" "$(ls /sys/class/net | sort | xargs)"
check "it resolves its own name" inside "getent hosts daniel"
inside 'sleep 1 &'  # left behind by a command that has ended
sleep 3
check "a process left behind is collected once it has ended" not_inside \
    "grep -l '^[0-9]* ([^)]*) Z' /proc/[0-9]*/stat"

step "A device connected after setup is handed over at the next start"
mknod /dev/daniel-test-device c 1 3   # a second node for the null device
check "the device is not in the container yet" not_inside "[ -e /dev/daniel-test-device ]"
check "the container starts again, within twenty seconds" timeout 20 sh -c \
    "systemctl restart daniel-body && docker exec daniel-body true"
check "the device is in the container" inside "[ -c /dev/daniel-test-device ]"
check "the device can be used" inside "echo x > /dev/daniel-test-device"

step "What Daniel has installed is kept; a device that has gone does not prevent the start"
inside 'for f in /usr/local/kept /etc/kept /var/lib/kept /opt/kept /root/kept /self/kept /tmp/lost; do echo x > $f; done'
rm -f /dev/daniel-test-device
check "the container starts again" restart_body
for kept in /usr/local/kept /etc/kept /var/lib/kept /opt/kept /root/kept /self/kept; do
    check "$kept is still there" inside "[ -e $kept ]"
done
check "/tmp starts empty" not_inside "[ -e /tmp/lost ]"
check "the device that has gone is no longer in the container" not_inside "[ -e /dev/daniel-test-device ]"

step "The container comes back by itself"
docker kill daniel-body >/dev/null 2>&1
check "it answers again within a minute" sh -c \
    'for _ in $(seq 60); do docker exec daniel-body true 2>/dev/null && exit 0; sleep 1; done; exit 1'
check "the wall still holds" sh "$FIXED/check-wall.sh"

step "The wall is tried by device numbers, whatever the names"
truncate -s 8M /tmp/daniel-test.img
loop=$(losetup --find --show /tmp/daniel-test.img)
restart_body
open_by_number() {  # as administrator, Daniel can make a node for any device number
    inside "rm -f /tmp/node; mknod /tmp/node b ${1%:*} ${1#*:} && head -c 1 /tmp/node >/dev/null"
}
cannot_open_by_number() { ! open_by_number "$1"; }
check "a device that is handed over can be opened through a node made by Daniel" \
    open_by_number "$(lsblk -nro MAJ:MIN "$loop" | head -1)"
check "the device that holds Linux cannot" cannot_open_by_number "$(mountpoint -d /)"
check "check-wall.sh tries the protected devices in the same way" sh -c \
    "sh '$FIXED/check-wall.sh' | grep -q 'holds  the protected device [0-9]*:[0-9]* cannot be opened'"
losetup --detach "$loop"

step "The loop wakes the mind, which acts in the container"
install -D -m 755 "$HERE/fake_claude.py" "$MIND/.local/bin/claude"
cat > "$MIND/replies" <<'REPLY'
{"calls": [{"name": "run", "arguments": {"command": "hostname"}}, {"name": "remember", "arguments": {"name": "first waking", "text": "I woke once."}}], "final": "I am here."}
REPLY
chown -R daniel-mind "$MIND/.local" "$MIND/replies"
sed -i 's/^DANIEL_MODEL=.*/DANIEL_MODEL=test-model-version/' /etc/daniel/daniel.env
printf 'FAKE_CLAUDE_REPLIES=%s\nFAKE_CLAUDE_RECORD=%s\n' "$MIND/replies" "$MIND/record" >> /etc/daniel/daniel.env
systemctl start daniel-loop
check "the mind has spoken within a minute" sh -c \
    "for _ in \$(seq 60); do grep -qs '\"last_words\": \"I am here.\"' $MIND/state.json && [ \$(wc -l < $MIND/record) -ge 2 ] && exit 0; sleep 1; done; exit 1"
systemctl stop daniel-loop
check "its tools acted in the container, and it was given back its last words, its latest actions and its memories" python3 - "$MIND/record" <<'PYTHON'
import json, sys
first, second = [json.loads(line) for line in open(sys.argv[1])][:2]
assert first["stdin"] == "Begin.", first["stdin"]
assert first["tools"] == ["run", "write", "remember", "recall"], first["tools"]
assert first["results"][0]["content"][0]["text"].startswith("daniel\n"), first["results"]
assert second["stdin"] == ("Your last words:\nI am here.\n\nYour latest actions:\nrun: hostname [exit code 0]\n"
    "remember: first waking\n\nYour memories, the strongest first:\n[first waking]\nI woke once."), second["stdin"]
PYTHON
step "A container made by an earlier version is set aside, not deleted"
systemctl stop daniel-body
docker run --detach --name daniel-body --restart always debian:stable-slim sleep infinity >/dev/null
docker exec daniel-body sh -c 'echo precious > /installed-by-daniel'
check "the service starts" systemctl start daniel-body
check "the new container answers, with what Daniel keeps" inside "[ -e /self/kept ] && [ -e /usr/local/kept ]"
check "the earlier container still exists, stopped for good" same \
    "$(docker container inspect --format '{{.State.Running}} {{.HostConfig.RestartPolicy.Name}}' daniel-body-old 2>&1)" "false no"
check "what Daniel had installed in it is still there" sh -c \
    "docker cp daniel-body-old:/installed-by-daniel - | tar -xO | grep -q precious"

[ "$failures" = 0 ] || journalctl -u daniel-loop -u daniel-body -n 40 --no-pager

printf '\n%s check(s) failed.\n' "$failures"
exit "$failures"
