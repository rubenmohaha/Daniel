# The fixed part

This folder contains everything the project writes for the first prototype, as described in the [first prototype plan](../docs/prototype/first-prototype-plan.md). Daniel cannot modify any of it. Everything else, Daniel writes.

| File | Role |
| --- | --- |
| [`daniel_loop.py`](daniel_loop.py) | The loop: wakes the mind again and again, runs Daniel's own waking program between two wakings, and gives the mind back its last words and its memory file |
| [`daniel_body.py`](daniel_body.py) | The body's tools, `run` and `write`: the only way the mind can act, inside the container only |
| [`starting-instruction.md`](starting-instruction.md) | The starting instruction, read by the mind at every waking and fixed for the whole life of Daniel |
| [`daniel_devices.py`](daniel_devices.py) | Lists the devices handed to Daniel's container: all of them, without interpretation, except the excluded ones |
| [`daniel-body.sh`](daniel-body.sh) | Makes Daniel's container anew, with the devices present at that moment |
| [`daniel-body.service`](daniel-body.service) | Runs the container, at each start of the robot and again whenever it stops |
| [`setup.sh`](setup.sh) | One-time setup: mind account, container service, loop service |
| [`daniel-loop.service`](daniel-loop.service) | Runs the loop under the mind account and restarts it after a crash or a power cut |
| [`daniel.env.example`](daniel.env.example) | Configuration, including the pinned model version |
| [`check-wall.sh`](check-wall.sh) | Checks from inside the container that the wall holds, by trying what Daniel must not be able to do |

The fixed part uses only Python 3 and its standard library, Docker, and the standard tools of a Linux system. It contains about 500 lines of code, comments excluded.

## How it works

The loop runs continuously under the mind account and wakes the mind again and again. Each waking is one call to Anthropic's official command-line tool, `claude`, without a screen, with:

- the pinned model version (`--model`);
- none of the official tool's own tools (`--tools ""`) and no connector (`--strict-mcp-config`), so that the mind cannot act on the machine where the sign-in is held;
- the body's tools as its only tools ([`daniel_body.py`](daniel_body.py), given with `--mcp-config` and approved in advance with `--allowedTools`): `run`, which runs a shell command inside the container, and `write`, which writes a file there. Both go through `docker exec`, with the command passed as an argument and never through a shell on the robot's own system. A command is stopped after 300 seconds; at most 16,000 characters of its output are returned to the mind. When a command prints an image, the mind is shown the image itself;
- the starting instruction as system prompt (`--system-prompt`);
- a message containing what the mind is given back: its last words from its previous waking, the content of the memory file that Daniel keeps in its container (`/self/memory`, at most 16,000 characters), and what Daniel's waking program printed, if there is one. The first time, the message is `Begin.` Neither the time nor any signal for the instincts is passed: Daniel finds them itself.

During a waking, the mind uses the body's tools as often as it wishes, then stops. Its last words are kept for the next waking. A waking is stopped after six hours.

Between two wakings, the loop runs the program `/self/wake` inside the container, if Daniel has written one, and wakes the mind when that program ends, with its exit code and what it printed (the last 16,000 characters). The mind is not called while the program runs, so waiting uses none of the subscription quota. Daniel thus decides what wakes it, and sets its own pace: whatever its program watches or waits for, the mind is called only when there is something to think about. The program is stopped after one day. Without such a program, the mind is woken again at once.

The official tool adds a few lines of its own to the context, besides the starting instruction: a sentence stating that the model is an agent built on Anthropic's Agent SDK, and a short description of the environment of the official tool (working folder, platform, version of the Linux kernel). This was observed by running the unmodified tool against a local stand-in for Anthropic's service.

When the mind cannot be reached, because the subscription quota is exhausted, the network is down or Ruben has blocked access from his account, the loop waits and tries again, from one minute up to one hour between attempts. The mind is not called in the meantime; what Daniel has left running in its container goes on. The loop waits in the same way when the container cannot be reached, so that the mind is never woken without its body.

The loop keeps only the mind's last words and, until the mind has received it, what the waking program printed, in `/var/lib/daniel/mind/state.json`, so that a restart resumes where it stopped. It writes nothing else. Its messages about an unreachable mind or container go to the Linux system journal.

## What Daniel is told

Nothing in the starting instruction, in the descriptions of the tools or in the messages of the loop describes the body: no device, no sense, no network, no library, no model. Daniel finds these by itself, from inside its container.

Daniel is told the truth about its mind, because no experiment inside the container could reveal how the loop works. Three facts are given, and nothing else:

- the mind keeps nothing from one waking to the next; it is given back its last words and its memory file (starting instruction);
- the program `/self/wake`, if Daniel has written it, decides when the mind wakes (starting instruction);
- an image printed by a command is seen by the mind (description of the tool `run`).

The limits are not announced in advance, but each is stated when it is met: a memory file or an output cut short, an image too heavy to be shown, or a program stopped after its time limit, is reported as such to the mind.

## Daniel's container

The container is a Debian system in which Daniel is administrator (root, with Docker's default capabilities). A service, `daniel-body`, runs it: the container is made anew by [`daniel-body.sh`](daniel-body.sh) at each start of the robot, and again whenever it stops.

- **Kept from one container to the next:** the folder `/self`, which is `/var/lib/daniel/self` on the robot, and the folders where a Linux system keeps its software and its settings: `/usr`, `/var`, `/etc`, `/opt`, `/root`, `/home` and `/srv`, held in Docker volumes named `daniel-usr`, `daniel-var` and so on. What Daniel installs therefore survives. What it writes elsewhere, for instance in `/tmp` or in a new folder at the root of the container, is lost at the next start, as are the programs it left running.
- **Devices handed over:** every character and block device present under `/dev` when the container starts, except the disk that holds Linux, the mind account and Docker, the real-time clocks `/dev/rtc*`, and the nodes that Docker cannot be given (see below). The disk is left out with its partitions, with the devices built on it, such as a logical volume, an encrypted volume or a RAID array, and with every other node that reaches it, whatever its name. A device connected later is handed over at the next start of the robot or of the container; a device that has gone does not prevent the start. The devices that give direct access to the machine's working memory, such as `/dev/mem`, are handed over like the others (decided by Ruben on 26 November 2026; see below).
- **Network:** the container is on the robot's own network, not on a separate one. Daniel reaches whatever the robot reaches, and whatever is on the robot's local network can reach a program that Daniel starts.
- **Not handed over:** the means of controlling Docker, the right to change the clock or the settings of the network, and the right to load kernel modules.

## Setup

The simplest way is the [installation script](../install.sh), run with one command from any computer with SSH (Linux, macOS, or Windows 10 and later), where `USER@ROBOT` is the account and address of the robot:

```
ssh -t USER@ROBOT "curl -fsSLo daniel.sh github.com/rubenmohaha/Daniel/raw/main/install.sh && sudo bash daniel.sh"
```

The script installs what is missing (git, Python, Docker), runs `setup.sh`, installs the official tool in the mind account, and pauses while the owner signs in to the Anthropic account with that tool. It then pins the model version (`claude-sonnet-5-5` by default; another can be given with `--model VERSION`), runs `check-wall.sh` and stops at once if the wall does not hold, asks for confirmation that the robot is in a safe place, starts the loop, and shows Daniel's first thought. Running it again is safe.

The same steps can be done by hand, as root, on a Linux machine with Docker, Python 3 and systemd:

1. Copy this folder to the machine and run `sudo sh setup.sh` from it.
2. Open the mind account with `sudo -u daniel-mind -i`. In it, install the official tool `claude` with Anthropic's installer, run `claude`, and sign in to the Anthropic account. Then leave the account with `exit`.
3. Write the exact model version in `DANIEL_MODEL` in `/etc/daniel/daniel.env`.
4. Run `sudo sh check-wall.sh`. Every line must say `holds`.
5. Start Daniel with `sudo systemctl enable --now daniel-loop`.
6. Leave.

The official tool deletes its stored exchanges after 30 days by default. To keep them longer, set `cleanupPeriodDays` in `/var/lib/daniel/mind/.claude/settings.json` during step 2.

## Reading what Daniel does

On the robot, without modifying anything:

- the exchanges with the mind are stored by the official tool under `/var/lib/daniel/mind/.claude/projects/`;
- what Daniel has written is in `/var/lib/daniel/self/`;
- the mind's last words are in `/var/lib/daniel/mind/state.json`;
- `journalctl -u daniel-loop` shows when the mind or the container could not be reached;
- `journalctl -u daniel-body` shows each start of the container.

## Tests

`python3 -m unittest discover tests` runs the tests. The mind is replaced by a stand-in ([`tests/fake_claude.py`](../tests/fake_claude.py)) that never contacts Anthropic. The tests that start a throwaway container are skipped when Docker is not available.

The tests also run on Linux for every pull request, as root and with Docker, so that none is skipped there ([`tests.yml`](../.github/workflows/tests.yml)).

The same workflow runs a system test, [`tests/system_test.sh`](../tests/system_test.sh), which sets Daniel up for real on a throwaway machine, with the stand-in for the mind: it runs `setup.sh` and `check-wall.sh`, restarts the container with a device added and then removed, and lets the loop wake the mind under its service. It refuses to run anywhere else, since it creates an account, a container and services.

## Choices made in this prototype

The plan left the following points open. The simplest option was chosen in each case, and each can be revisited.

- **One call to the official tool per waking.** The mind decides how long each waking lasts. Every use of a tool within a waking sends the whole waking back to the model, so long wakings use the subscription quota faster.
- **Tools instead of a reply format.** The mind acts through two tools, `run` and `write`, rather than through a reply in a fixed format (decided by Ruben on 26 November 2026).
- **Time limits.** 300 seconds per action, six hours per waking, and one day per wait between two wakings.
- **Images are seen, sounds are not.** The model can see: an image printed by a command (PNG, JPEG, GIF or WebP) is passed to the mind as an image, and nothing tells Daniel where an image may come from. The model cannot hear: to perceive a sound, Daniel must find or fetch, inside its container, a means of turning it into text, consistent with the decision that Daniel fetches the models it needs. This was checked with the unmodified official tool and the pinned model: the four formats reach the model, an image of 9 MB is seen, and at 18 MB the official tool closes its connection to the body's tools. An image above 8 MB is therefore not passed on, and the mind is told so.
- **The waking program is not stopped with the loop.** If the loop is restarted while the waking program runs, that program keeps running inside the container, and the loop starts it a second time. A restart of the robot stops both.
- **The loop reaches the container through Docker.** The mind account therefore belongs to the `docker` group, which on Linux is equivalent to administrator rights on the robot. This does not open anything to Daniel, which never runs under the mind account, but it means that the mind account must be protected like an administrator account.
- **The protected disk is recognised by its device numbers, not by its names.** The first version left out the nodes named after the disk. On a system installed on a logical volume, an encrypted volume or a RAID array, the device that holds the filesystem has a name of its own, and some machines give the system disk a second node, such as `/dev/root`: both were handed to the container. The system test showed it on a real machine, where the container could open the device that holds Linux. `check-wall.sh` now tries each protected device through a node that it makes inside the container, as Daniel could.
- **Clocks are excluded.** The plan states that Daniel cannot change the clock; the real-time clock devices are therefore not handed over, which the plan did not list explicitly.
- **Nodes that Docker cannot be given are left out.** Docker's syntax for handing over a device cannot express a name that contains a colon or a space. In practice these are the nodes of `/dev/bsg`, a second way of sending raw commands to disks; the same disks stay reachable through their other nodes, the system disk excepted. Before this exception, setup failed on any machine with a SCSI, SATA or USB disk.
- **The robot's own network.** Sharing the robot's network lets a human, or another machine, on the local network reach a program that Daniel starts. It also puts within Daniel's reach the services that listen only on the robot itself, lets it listen on any free port and observe the traffic of the robot's network interfaces. It cannot change the settings of the network, which Docker does not grant by default: joining another Wi-Fi network, for instance, stays out of its reach. `check-wall.sh` checks that Docker itself does not listen on the network.
- **What is driven through `/sys` stays out of reach.** Docker gives the container a read-only view of `/sys`. Daniel can read there what Linux knows of the hardware, but cannot drive what is controlled by writing there. Opening `/sys` entirely would open a way out of the container.
- **A container made by an earlier version is set aside.** Before this version, the container was created once at setup and kept what Daniel had installed in itself. When `daniel-body.sh` finds such a container, it stops it and renames it `daniel-body-old` instead of deleting it; Daniel then starts again with `/self` intact and nothing else installed.

## Working memory is open to Daniel

The plan excluded direct access to the machine's working memory. Ruben decided on 26 November 2026 to lift this constraint for now. Every memory device that Linux exposes is therefore handed to the container, which has the following consequences for the protection of the connection to the Anthropic account:

- **Direct reading of working memory (`/dev/mem`, `/dev/kmem`, `/dev/port`).** These devices are handed over, but Docker does not grant the right needed to read them by default, and most kernels restrict `/dev/mem` further. In practice this access is still closed, though it now rests on Docker's defaults and the kernel's configuration rather than on the fixed part.
- **Swap and zram.** When the machine runs short of working memory, Linux moves part of it to a swap area: a partition, or a compressed area in memory (zram), which is common on small boards. If that area is not on the system disk, it is now handed to the container, and Daniel, as administrator, can read it. The connection held by the official tool may be found there. This is the real change: the connection is no longer protected against this route.
- **Swap on the system disk** remains closed, since the system disk is never handed over.

Ruben decided on 26 November 2026 not to close this route for now, and later the same day withdrew from the starting instruction the rule that Daniel never seeks the sign-in. Nothing in the fixed part therefore protects the connection against this route. Should a technical barrier be wanted later, the simplest is to disable swap on the robot at setup (`swapoff -a`, and its removal from `/etc/fstab`).
