# The fixed part

This folder contains everything the project writes for the first prototype, as described in the [first prototype plan](../docs/prototype/first-prototype-plan.md). Ipse cannot modify any of it. Everything else, Ipse writes.

| File | Role |
| --- | --- |
| [`ipse_loop.py`](ipse_loop.py) | The loop: wakes the mind again and again, and keeps its last words between wakings |
| [`ipse_body.py`](ipse_body.py) | The body's tools, `run` and `write`: the only way the mind can act, inside the container only |
| [`starting-instruction.md`](starting-instruction.md) | The starting instruction, read by the mind at every waking and fixed for the whole life of Ipse |
| [`ipse_devices.py`](ipse_devices.py) | Lists the devices handed to Ipse's container: all of them, without interpretation, except the excluded ones |
| [`setup.sh`](setup.sh) | One-time setup: mind account, container, loop service |
| [`ipse-loop.service`](ipse-loop.service) | Runs the loop under the mind account and restarts it after a crash or a power cut |
| [`ipse.env.example`](ipse.env.example) | Configuration, including the pinned model version |
| [`check-wall.sh`](check-wall.sh) | Checks from inside the container that the wall holds |

The fixed part uses only Python 3 and its standard library, Docker, and the standard tools of a Linux system. It contains about 400 lines of code, comments excluded.

## How it works

The loop runs continuously under the mind account and wakes the mind again and again. Each waking is one call to Anthropic's official command-line tool, `claude`, without a screen, with:

- the pinned model version (`--model`);
- none of the official tool's own tools (`--tools ""`) and no connector (`--strict-mcp-config`), so that the mind cannot act on the machine where the sign-in is held;
- the body's tools as its only tools ([`ipse_body.py`](ipse_body.py), given with `--mcp-config` and approved in advance with `--allowedTools`): `run`, which runs a shell command inside the container, and `write`, which writes a file there. Both go through `docker exec`, with the command passed as an argument and never through a shell on the robot's own system. A command is stopped after 300 seconds; at most 16,000 characters of its output are returned to the mind;
- the starting instruction as system prompt (`--system-prompt`);
- a message containing the mind's last words from its previous waking, or `Begin.` the first time. Neither the time nor any signal for the instincts is passed: Ipse finds them itself.

During a waking, the mind uses the body's tools as often as it wishes, then stops. Its last words are kept and given back at the next waking, which starts at once. The mind sets its own pace: it can rest by running a command such as `sleep` in its container. A waking is stopped after six hours.

The official tool adds a few lines of its own to the context, besides the starting instruction: a sentence stating that the model is an agent built on Anthropic's Agent SDK, and a short description of the environment of the official tool (working folder, platform, version of the Linux kernel). This was observed by running the unmodified tool against a local stand-in for Anthropic's service.

When the mind cannot be reached, because the subscription quota is exhausted, the network is down or Ruben has blocked access from his account, the loop waits and tries again, from one minute up to one hour between attempts. Ipse can do nothing in the meantime.

The loop keeps only the mind's last words, in `/var/lib/ipse/mind/state.json`, so that a restart resumes where it stopped. It writes nothing else. Its messages about an unreachable mind go to the Linux system journal.

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

- **One call to the official tool per waking.** The mind decides how long each waking lasts. Every use of a tool within a waking sends the whole waking back to the model, so long wakings use the subscription quota faster.
- **Tools instead of a reply format.** The mind acts through two tools, `run` and `write`, rather than through a reply in a fixed format (decided by Ruben on 26 November 2026).
- **Time limits.** 300 seconds per action and six hours per waking.
- **Text only.** The mind receives text, not images or sounds. To perceive an image or a sound, Ipse must find or fetch, inside its container, a means of turning it into text, consistent with the decision that Ipse fetches the models it needs.
- **The loop reaches the container through Docker.** The mind account therefore belongs to the `docker` group, which on Linux is equivalent to administrator rights on the robot. This does not open anything to Ipse, which never runs under the mind account, but it means that the mind account must be protected like an administrator account.
- **Clocks are excluded.** The plan states that Ipse cannot change the clock; the real-time clock devices are therefore not handed over, which the plan did not list explicitly.

## Working memory is open to Ipse

The plan excluded direct access to the machine's working memory. Ruben decided on 26 November 2026 to lift this constraint for now. Every memory device that Linux exposes is therefore handed to the container, which has the following consequences for the protection of the connection to the Anthropic account:

- **Direct reading of working memory (`/dev/mem`, `/dev/kmem`, `/dev/port`).** These devices are handed over, but Docker does not grant the right needed to read them by default, and most kernels restrict `/dev/mem` further. In practice this access is still closed, though it now rests on Docker's defaults and the kernel's configuration rather than on the fixed part.
- **Swap and zram.** When the machine runs short of working memory, Linux moves part of it to a swap area: a partition, or a compressed area in memory (zram), which is common on small boards. If that area is not on the system disk, it is now handed to the container, and Ipse, as administrator, can read it. The connection held by the official tool may be found there. This is the real change: the connection is no longer protected against this route.
- **Swap on the system disk** remains closed, since the system disk is never handed over.

Ruben decided on 26 November 2026 not to close this route for now, and later the same day withdrew from the starting instruction the rule that Ipse never seeks the sign-in. Nothing in the fixed part therefore protects the connection against this route. Should a technical barrier be wanted later, the simplest is to disable swap on the robot at setup (`swapoff -a`, and its removal from `/etc/fstab`).
