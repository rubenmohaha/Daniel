#!/bin/bash
# One-command installation of Daniel on a robot running Linux.
#
# From any computer with SSH (Linux, macOS, or Windows 10 and later):
#
#   ssh -t USER@ROBOT "curl -fsSLo daniel.sh github.com/rubenmohaha/Daniel/raw/main/install.sh && sudo bash daniel.sh"
#
# The script is saved before it runs, rather than piped into sudo: on systems
# where sudo opens its own terminal, a piped script could not ask questions.
#
# The script installs what is missing, sets up the fixed part, waits while the
# owner signs in to their Anthropic account with the official tool, pins the
# model version, checks the wall, and starts Daniel. It stops at once if the
# wall does not hold. It never reads the credentials of the official tool.
#
# Options, given after "daniel.sh": --model VERSION (default at first
# installation: claude-sonnet-5-5; kept unchanged on later runs unless
# given), --yes (do not ask for confirmation before starting). Running it
# again is safe: what is already in place is left unchanged.
#
# The whole script is a function called on the last line, so that it is read
# completely before anything runs.
main() {
set -euo pipefail

MODEL=
ASK=1
while [ $# -gt 0 ]; do
    case "$1" in
        --model) MODEL="$2"; shift 2 ;;
        --yes) ASK=0; shift ;;
        *) echo "Unknown option: $1" >&2; exit 2 ;;
    esac
done

REPO=https://github.com/rubenmohaha/Daniel.git
SOURCE=/opt/daniel-source
MIND_USER=daniel-mind
CLAUDE=/var/lib/daniel/mind/.local/bin/claude

as_mind() { sudo -u "$MIND_USER" -H bash -c 'cd ~ && exec "$@"' bash "$@"; }
step() { printf '\n==> %s\n' "$1"; }
fail() { printf '\nSTOPPED: %s\n' "$1" >&2; exit 1; }

[ "$(id -u)" = 0 ] || fail "run this script with sudo"
command -v systemctl >/dev/null || fail "this Linux system does not use systemd"
{ : </dev/tty; } 2>/dev/null || fail "no terminal: connect with 'ssh -t' so that questions can be answered"
# The terminal, by its own name. On systems where sudo opens a terminal of its
# own, sudo passes on what is typed only to a program that reads from the very
# terminal sudo was started from: read through /dev/tty, the sign-in code would
# be shown on the screen and never reach the official tool.
terminal=/dev/$(ps -o tty= -p $$ 2>/dev/null | tr -d ' ')
[ -c "$terminal" ] || terminal=/dev/tty

step "1/7 Installing what is missing (git, Python, Docker)"
if command -v apt-get >/dev/null; then
    missing=""
    for tool in git python3 curl findmnt; do command -v "$tool" >/dev/null || missing="$missing $tool"; done
    if [ -n "$missing" ]; then
        apt-get update -qq
        apt-get install -y -qq git python3 curl util-linux >/dev/null
    fi
fi
for tool in git python3 curl findmnt lsblk; do
    command -v "$tool" >/dev/null || fail "missing: $tool (install it, then run this script again)"
done
if ! command -v docker >/dev/null; then
    curl -fsSL https://get.docker.com | sh >/dev/null
fi
systemctl enable --now docker >/dev/null 2>&1 || true
docker info >/dev/null 2>&1 || fail "Docker is installed but not running"
echo "ok"

step "2/7 Fetching Daniel"
if [ -d "$SOURCE/.git" ]; then
    git -C "$SOURCE" pull -q --ff-only
else
    git clone -q --depth 1 "$REPO" "$SOURCE"
fi
echo "ok ($(git -C "$SOURCE" rev-parse --short HEAD))"

step "3/7 Setting up the mind account and Daniel's container"
(cd "$SOURCE/fixed" && DANIEL_QUIET=1 sh setup.sh)
echo "ok"

step "4/7 Installing the official tool in the mind account"
if [ ! -x "$CLAUDE" ]; then
    as_mind bash -c 'curl -fsSL https://claude.ai/install.sh | bash' >/dev/null
fi
[ -x "$CLAUDE" ] || fail "the official tool could not be installed"
echo "ok"

step "5/7 Signing in to the Anthropic account"
signed_in() { as_mind "$CLAUDE" auth status 2>/dev/null | grep -q '"loggedIn": *true'; }
if signed_in; then
    echo "already signed in"
else
    echo "Sign in with your Claude subscription. If the robot has no screen, open the"
    echo "link shown below on your own computer, then paste the code back here."
    as_mind "$CLAUDE" auth login --claudeai <"$terminal"
    signed_in || fail "the sign-in did not succeed; run this script again to retry"
    echo "ok"
fi

step "6/7 Pinning the model version and checking the wall"
current=$(sed -n 's/^DANIEL_MODEL=//p' /etc/daniel/daniel.env)
if [ -n "$MODEL" ] || [ -z "$current" ]; then
    MODEL=${MODEL:-claude-sonnet-5-5}
    sed -i "s|^DANIEL_MODEL=.*|DANIEL_MODEL=$MODEL|" /etc/daniel/daniel.env
    current=$MODEL
fi
echo "model: $current"
if ! sh "$SOURCE/fixed/check-wall.sh"; then
    systemctl stop daniel-loop 2>/dev/null || true
    fail "the wall does not hold; Daniel was not started (or was stopped)"
fi

step "7/7 Starting Daniel"
if [ "$ASK" = 1 ]; then
    echo "Daniel has no fixed reflex. Before starting, place the robot somewhere safe"
    echo "(wheels off the ground or in an enclosure) and inform the people nearby."
    read -r -p "Is the robot in a safe place? Type yes to start: " answer </dev/tty
    [ "$answer" = yes ] || fail "not started; run this script again when ready"
fi
systemctl enable daniel-loop >/dev/null 2>&1
systemctl restart daniel-loop
printf 'Waiting for Daniel to wake up'
for _ in $(seq 1 36); do
    if grep -qs '"last_words": "' /var/lib/daniel/mind/state.json || \
       find /var/lib/daniel/mind/.claude/projects -name '*.jsonl' 2>/dev/null | grep -q .; then
        cat <<DONE


Daniel is awake.

Follow Daniel on a page: http://$(hostname -I 2>/dev/null | cut -d' ' -f1):$(sed -n 's/^DANIEL_VIEW_PORT=//p' /etc/daniel/daniel.env | grep . || echo 8642)
                         (from the local network; it only shows, and has no button)
Read what Daniel does:   sudo ls -R /var/lib/daniel/self
                         sudo cat /var/lib/daniel/mind/state.json      (its last words)
                         sudo cat /var/lib/daniel/mind/journal         (its actions)
                         sudo cat /var/lib/daniel/mind/memories.json   (its memories)
                         sudo ls /var/lib/daniel/mind/.claude/projects/ (its full exchanges)
Stop Daniel entirely:    sudo systemctl disable --now daniel-loop daniel-body
DONE
        exit 0
    fi
    printf '.'; sleep 5
done
printf '\n'
journalctl -u daniel-loop -n 20 --no-pager
fail "Daniel did not wake up within 3 minutes; the lines above say why"
}

main "$@" </dev/null
