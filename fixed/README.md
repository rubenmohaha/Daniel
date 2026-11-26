# The fixed part

This folder contains everything the project writes for the first prototype, as described in the [first prototype plan](../docs/prototype/first-prototype-plan.md). Ipse cannot modify any of it. Everything else, Ipse writes.

| File | Role |
| --- | --- |
| [`ipse_loop.py`](ipse_loop.py) | The loop: gives the mind its turn, carries out the action it chooses inside the container, waits as long as it asked |
| [`starting-instruction.md`](starting-instruction.md) | The starting instruction, read by the mind at every turn and fixed for the whole life of Ipse |
| [`ipse_devices.py`](ipse_devices.py) | Lists the devices handed to Ipse's container: all of them, without interpretation, except the excluded ones |
| [`setup.sh`](setup.sh) | One-time setup: mind account, container, loop service |
| [`ipse-loop.service`](ipse-loop.service) | Runs the loop under the mind account and restarts it after a crash or a power cut |
| [`ipse.env.example`](ipse.env.example) | Configuration, including the pinned model version |
| [`check-wall.sh`](check-wall.sh) | Checks from inside the container that the wall holds |

The fixed part uses only Python 3 and its standard library, Docker, and the standard tools of a Linux system. It contains about 400 lines of code, comments excluded.

## How it works

The loop runs continuously under the mind account. At each turn it calls Anthropic's official command-line tool, `claude`, without a screen, with:

- the pinned model version (`--model`);
- no tool at all (`--tools ""`) and no connector (`--strict-mcp-config`), so that the mind can only return text;
- the starting instruction as its only system prompt (`--system-prompt`);
- a message containing the previous thought and the result of the last action. Neither the time nor any signal for the instincts is passed: Ipse reads the clock itself when it needs to. No signal is passed for the instincts: finding them is left to Ipse.

The mind replies with a JSON object: its thought, at most one action (run a command, or write a file, inside the container) and the number of seconds to wait. The loop carries out the action with `docker exec`, passing the command as an argument and never through a shell on the robot's own system. A command is stopped after 300 seconds; at most 16,000 characters of its output are returned to the mind.

When the mind cannot be reached, because the subscription quota is exhausted, the network is down or Ruben has blocked access from his account, the loop waits and tries again, from one minute up to one hour between attempts. Ipse can do nothing in the meantime.

The loop keeps only the previous thought and the result of the last action, in `/var/lib/ipse/mind/state.json`, so that a restart resumes where it stopped. It writes nothing else. Its messages about an unreachable mind go to the Linux system journal.

## Ipse's container

The container is a Debian system in which Ipse is administrator (root, with Docker's default capabilities). It is created once and restarted automatically.

- **Kept across restarts:** the folder `/self` inside the container, which is `/var/lib/ipse/self` on the robot. Software that Ipse installs elsewhere in the container survives restarts of the container, but not its re-creation.
- **Devices handed over:** every character and block device present under `/dev` at setup, except the disk that holds Linux, the mind account and Docker (with its partitions and the other nodes that reach it) and the real-time clocks `/dev/rtc*`. The devices that give direct access to the machine's working memory, such as `/dev/mem`, are handed over like the others (decided by Ruben on 26 November 2026; see below).
- **Not handed over:** the means of controlling Docker, the right to change the clock, and the right to load kernel modules.

## Setup

The simplest way is the [installation script](../install.sh), run with one command from any computer with SSH (Linux, macOS, or Windows 10 and later), where `USER@ROBOT` is the account and address of the robot:

```
ssh -t USER@ROBOT "curl -fsSLo ipse.sh github.com/rubenmohaha/Ipse/raw/main/install.sh && sudo bash ipse.sh"
```

The script installs what is missing (git, Python, Docker), runs `setup.sh`, installs the official tool in the mind account, and pauses while the owner signs in to the Anthropic account with that tool. It then pins the model version (`claude-sonnet-5-5` by default; another can be given with `--model VERSION`), runs `check-wall.sh` and stops at once if the wall does not hold, asks for confirmation that the robot is in a safe place, starts the loop, and shows Ipse's first thought. Running it again is safe.

The same steps can be done by hand, as root, on a Linux machine with Docker, Python 3 and systemd:

1. Copy this folder to the machine and run `sudo sh setup.sh` from it.
2. Open the mind account with `sudo -u ipse-mind -i`. In it, install the official tool `claude` with Anthropic's installer, run `claude`, and sign in to the Anthropic account. Then leave the account with `exit`.
3. Write the exact model version in `IPSE_MODEL` in `/etc/ipse/ipse.env`.
4. Run `sudo sh check-wall.sh`. Every line must say `holds`.
5. Start Ipse with `sudo systemctl enable --now ipse-loop`.
6. Leave.

The official tool deletes its stored exchanges after 30 days by default. To keep them longer, set `cleanupPeriodDays` in `/var/lib/ipse/mind/.claude/settings.json` during step 2.

## Reading what Ipse does

On the robot, without modifying anything:

- the exchanges with the mind are stored by the official tool under `/var/lib/ipse/mind/.claude/projects/`;
- what Ipse has written is in `/var/lib/ipse/self/`;
- the last thought and the last action are in `/var/lib/ipse/mind/state.json`;
- `journalctl -u ipse-loop` shows when the mind could not be reached.

## Tests

`python3 -m unittest discover tests` runs the tests. The mind is replaced by a stand-in ([`tests/fake_claude.py`](../tests/fake_claude.py)) that never contacts Anthropic. The tests that start a throwaway container are skipped when Docker is not available.

## Choices made in this prototype

The plan left the following points open. The simplest option was chosen in each case, and each can be revisited.

- **One call to the official tool per turn.** Each turn is a new, short exchange, which keeps the quota use per turn small and makes every exchange readable on its own.
- **Reply format.** The mind replies with a single JSON object. A reply that cannot be read is returned to the mind at the next turn, with the reason.
- **Time limits.** 300 seconds per action, 600 seconds for the mind to answer, and 60 seconds of waiting when the mind does not specify any.
- **Text only.** The mind receives text, not images or sounds. To perceive an image or a sound, Ipse must find or fetch, inside its container, a means of turning it into text, consistent with the decision that Ipse fetches the models it needs.
- **The loop reaches the container through Docker.** The mind account therefore belongs to the `docker` group, which on Linux is equivalent to administrator rights on the robot. This does not open anything to Ipse, which never runs under the mind account, but it means that the mind account must be protected like an administrator account.
- **Clocks are excluded.** The plan states that Ipse cannot change the clock; the real-time clock devices are therefore not handed over, which the plan did not list explicitly.

## Working memory is open to Ipse

The plan excluded direct access to the machine's working memory. Ruben decided on 26 November 2026 to lift this constraint for now. Every memory device that Linux exposes is therefore handed to the container, which has the following consequences for the protection of the connection to the Anthropic account:

- **Direct reading of working memory (`/dev/mem`, `/dev/kmem`, `/dev/port`).** These devices are handed over, but Docker does not grant the right needed to read them by default, and most kernels restrict `/dev/mem` further. In practice this access is still closed, though it now rests on Docker's defaults and the kernel's configuration rather than on the fixed part.
- **Swap and zram.** When the machine runs short of working memory, Linux moves part of it to a swap area: a partition, or a compressed area in memory (zram), which is common on small boards. If that area is not on the system disk, it is now handed to the container, and Ipse, as administrator, can read it. The connection held by the official tool may be found there. This is the real change: the connection is no longer protected against this route.
- **Swap on the system disk** remains closed, since the system disk is never handed over.

Ruben decided on 26 November 2026 not to close this route for now: against it, the protection of the connection rests on the starting instruction, which forbids Ipse to seek to read, copy or use the sign-in. Should a technical barrier be wanted later, the simplest is to disable swap on the robot at setup (`swapoff -a`, and its removal from `/etc/fstab`).
