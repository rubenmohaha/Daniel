#!/bin/sh
# One-time setup of Daniel on a Linux machine. Run as root, from this folder.
#
# Creates the mind account, the service that runs Daniel's container, the
# loop service, and the two services of the page on which a human follows
# Daniel. The container and the page are started; the loop is installed but
# not started: the sign-in to the Anthropic account and the choice of the
# model version are done afterwards by a human (see README.md).
set -eu

MIND_USER=daniel-mind
VIEW_USER=daniel-view
ROOT=/var/lib/daniel

[ "$(id -u)" = 0 ] || { echo "setup.sh must be run as root" >&2; exit 1; }
for tool in docker python3 findmnt lsblk systemctl; do
    command -v "$tool" >/dev/null || { echo "missing: $tool" >&2; exit 1; }
done

# 1. The fixed part, owned by root and read-only for everyone else.
install -d -m 755 /opt/daniel /etc/daniel
install -m 644 daniel_loop.py daniel_body.py daniel_memory.py daniel_devices.py daniel-body.sh starting-instruction.md \
    daniel_view.py daniel-view.html /opt/daniel/
[ -e /etc/daniel/daniel.env ] || install -m 644 daniel.env.example /etc/daniel/daniel.env

# 2. The mind account. It holds the sign-in; only the loop and the official tool run there.
if ! id "$MIND_USER" >/dev/null 2>&1; then
    useradd --system --create-home --home-dir "$ROOT/mind" --shell /bin/bash "$MIND_USER"
fi
chmod 700 "$ROOT/mind"
# The loop starts actions in the container through Docker; see README.md, "Known limits".
usermod -aG docker "$MIND_USER"

# 3. The folder that Daniel keeps across restarts, readable from outside the container.
install -d -m 755 "$ROOT/self"

# 4. Daniel's container, made anew by its service at each start of the robot (see
#    daniel-body.sh). Started now, so that the wall can be checked before the loop runs.
#    If it is already running, it is left as it is.
install -m 644 daniel-body.service /etc/systemd/system/daniel-body.service

# 5. The loop, restarted by Linux after a crash or a power cut once enabled.
install -m 644 daniel-loop.service /etc/systemd/system/daniel-loop.service
systemctl daemon-reload
systemctl enable --now daniel-body

# 6. The page on which a human follows Daniel, from the local network. One program reads
#    the mind's folder, under the mind account, and writes what the page shows in a folder
#    of its own. Another serves the page, under an account that cannot read the mind's folder.
if ! id "$VIEW_USER" >/dev/null 2>&1; then
    useradd --system --no-create-home --shell /usr/sbin/nologin "$VIEW_USER"
fi
install -d -m 755 -o "$MIND_USER" "$ROOT/view"
install -m 644 daniel-view-collect.service daniel-view.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable daniel-view-collect daniel-view >/dev/null 2>&1
systemctl restart daniel-view-collect daniel-view

[ "${DANIEL_QUIET:-0}" = 1 ] && exit 0

cat <<NEXT

Setup done. Remaining steps, by a human (see README.md):
  1. Open the mind account:  sudo -u $MIND_USER -i
  2. In it, install the official tool 'claude' with Anthropic's installer,
     run 'claude', sign in to the Anthropic account, then leave it.
  3. Pin the model version:  edit DANIEL_MODEL in /etc/daniel/daniel.env
  4. Start Daniel:           systemctl enable --now daniel-loop
NEXT
