#!/bin/sh
# One-time setup of Ipse on a Linux machine. Run as root, from this folder.
#
# Creates the mind account, Ipse's container and the loop service. The loop is
# installed but not started: the sign-in to the Anthropic account and the
# choice of the model version are done afterwards by a human (see README.md).
set -eu

MIND_USER=ipse-mind
CONTAINER=ipse-body
IMAGE=debian:stable-slim
ROOT=/var/lib/ipse

[ "$(id -u)" = 0 ] || { echo "setup.sh must be run as root" >&2; exit 1; }
for tool in docker python3 findmnt lsblk systemctl; do
    command -v "$tool" >/dev/null || { echo "missing: $tool" >&2; exit 1; }
done

# 1. The fixed part, owned by root and read-only for everyone else.
install -d -m 755 /opt/ipse /etc/ipse
install -m 644 ipse_loop.py ipse_body.py ipse_devices.py starting-instruction.md /opt/ipse/
[ -e /etc/ipse/ipse.env ] || install -m 644 ipse.env.example /etc/ipse/ipse.env

# 2. The mind account. It holds the sign-in; only the loop and the official tool run there.
if ! id "$MIND_USER" >/dev/null 2>&1; then
    useradd --system --create-home --home-dir "$ROOT/mind" --shell /bin/bash "$MIND_USER"
fi
chmod 700 "$ROOT/mind"
# The loop starts actions in the container through Docker; see README.md, "Known limits".
usermod -aG docker "$MIND_USER"

# 3. The folder that Ipse keeps across restarts, readable from outside the container.
install -d -m 755 "$ROOT/self"

# 4. Ipse's container: administrator inside, every device but the excluded ones,
#    no access to the system disk, to working memory, to the clock or to Docker.
if docker container inspect "$CONTAINER" >/dev/null 2>&1; then
    echo "container $CONTAINER already exists; left unchanged"
else
    devices=$(python3 /opt/ipse/ipse_devices.py)
    # shellcheck disable=SC2086  # one --device argument per line, no spaces
    docker run --detach --name "$CONTAINER" --hostname ipse \
        --restart always --init \
        --volume "$ROOT/self:/self" --workdir /self \
        $devices \
        "$IMAGE" sleep infinity
fi

# 5. The loop, restarted by Linux after a crash or a power cut once enabled.
install -m 644 ipse-loop.service /etc/systemd/system/ipse-loop.service
systemctl daemon-reload

[ "${IPSE_QUIET:-0}" = 1 ] && exit 0

cat <<NEXT

Setup done. Remaining steps, by a human (see README.md):
  1. Open the mind account:  sudo -u $MIND_USER -i
  2. In it, install the official tool 'claude' with Anthropic's installer,
     run 'claude', sign in to the Anthropic account, then leave it.
  3. Pin the model version:  edit IPSE_MODEL in /etc/ipse/ipse.env
  4. Start Ipse:             systemctl enable --now ipse-loop
NEXT
