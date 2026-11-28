# The fixed part

This folder contains everything the project writes for the first prototype, as described in the [first prototype plan](../docs/prototype/first-prototype-plan.md). Daniel cannot modify any of it. Everything else, Daniel writes.

| File | Role |
| --- | --- |
| [`daniel_loop.py`](daniel_loop.py) | The loop: wakes the mind again and again, runs Daniel's own waking program between two wakings, and gives the mind back its last words, its latest actions and its strongest memories |
| [`daniel_memory.py`](daniel_memory.py) | The mind's memories and the journal of its actions: what is recent or used often comes back by itself, the rest must be looked for |
| [`daniel_body.py`](daniel_body.py) | The mind's tools: `run` and `write`, the only way it can act, inside the container only, and `remember` and `recall`, for its memories. Runs Daniel's feeling program after each action |
| [`starting-instruction.md`](starting-instruction.md) | The starting instruction, read by the mind at every waking and fixed for the whole life of Daniel |
| [`daniel_devices.py`](daniel_devices.py) | Lists the devices handed to Daniel's container: all of them, without interpretation, except the excluded ones |
| [`daniel-body.sh`](daniel-body.sh) | Makes Daniel's container anew, with the devices present at that moment |
| [`daniel-body.service`](daniel-body.service) | Runs the container, at each start of the robot and again whenever it stops |
| [`setup.sh`](setup.sh) | One-time setup: mind account, container service, loop service |
| [`daniel-loop.service`](daniel-loop.service) | Runs the loop under the mind account and restarts it after a crash or a power cut |
| [`daniel.env.example`](daniel.env.example) | Configuration, including the pinned model version |
| [`check-wall.sh`](check-wall.sh) | Checks from inside the container that the wall holds, by trying what Daniel must not be able to do |
| [`daniel_view.py`](daniel_view.py) | The page on which a human follows Daniel: one program reads what the mind has recorded, another serves the page on the local network |
| [`daniel-view.html`](daniel-view.html) | The page itself: one screen, drawn again every few seconds, without a button |
| [`daniel-view-collect.service`](daniel-view-collect.service), [`daniel-view.service`](daniel-view.service) | Run the two programs of the page, each under its own account |

The fixed part uses only Python 3 and its standard library, Docker, and the standard tools of a Linux system. The loop, the body's tools, the memories and the setup contain about 700 lines of code, comments excluded; the page adds about 700, half of them in the page itself.

## How it works

The loop runs continuously under the mind account and wakes the mind again and again. Each waking is one call to Anthropic's official command-line tool, `claude`, without a screen, with:

- the pinned model version (`--model`);
- none of the official tool's own tools (`--tools ""`) and no connector (`--strict-mcp-config`), so that the mind cannot act on the machine where the sign-in is held;
- the body's tools as its only tools ([`daniel_body.py`](daniel_body.py), given with `--mcp-config` and approved in advance with `--allowedTools`): `run`, which runs a shell command inside the container, and `write`, which writes a file there. Both go through `docker exec`, with the command passed as an argument and never through a shell on the robot's own system. A command is stopped after 300 seconds; at most 16,000 characters of its output are returned to the mind. When a command prints an image, the mind is shown the image itself;
- the starting instruction as system prompt (`--system-prompt`);
- a size beyond which the official tool sums up the thread of the waking (`--autocompact 200000`, in tokens; see below);
- a request that the official tool keep, in the exchanges it stores, a summary of the mind's reasoning (`--thinking-display summarized`; see [Reading what Daniel does](#reading-what-daniel-does));
- a message containing what the mind is given back: its last words from its previous waking, its latest actions (at most 4,000 characters), the strongest of its memories (at most 16,000 characters, then names only), and what Daniel's waking program printed, if there is one. The first time, the message is `Begin.` The time is not passed, and the fixed part supplies no signal of its own for the instincts: what Daniel feels is what its own program prints (see below).

During a waking, the mind uses the body's tools as often as it wishes, then stops. Its last words are kept for the next waking. A waking is cut after six hours; the mind is told so at its next waking, in place of its last words, so that it does not start the same waking again.

Every use of a tool sends the whole thread of the waking back to the model. When that thread nears 200,000 tokens, the official tool replaces it by a summary that it writes itself, and the waking goes on with the starting instruction unchanged. Left to itself, the tool would wait until the thread nears the limit of the model, which is a million tokens on the model pinned by default. The summary lives only as long as the waking: what must last belongs in a memory.

Between two wakings, the loop runs the program `/self/wake` inside the container, if Daniel has written one, and wakes the mind when that program ends, with its exit code and what it printed (the last 16,000 characters). The mind is not called while the program runs, so waiting uses none of the subscription quota. Daniel thus decides what wakes it, and sets its own pace: whatever its program watches or waits for, the mind is called only when there is something to think about. The program is stopped after one day. Without such a program, the mind is woken again at once.

After each `run` or `write`, and at each waking, the fixed part runs the program `/self/feel` inside the container, if Daniel has written one, and gives the mind what it printed, under the words `You feel:`. Nothing is added when the program prints nothing. The program is stopped after 10 seconds, and at most 2,000 characters are given. This is how an instinct receives a signal without anything of the body being described: Daniel finds the readings, and the fixed part only carries what its program reports.

The official tool adds a few lines of its own to the context, besides the starting instruction: a sentence stating that the model is an agent built on Anthropic's Agent SDK, and a short description of the environment of the official tool (working folder, platform, version of the Linux kernel). This was observed by running the unmodified tool against a local stand-in for Anthropic's service.

When the mind cannot be reached, because the subscription quota is exhausted, the network is down or Ruben has blocked access from his account, the loop waits and tries again, from one minute up to one hour between attempts. The mind is not called in the meantime; what Daniel has left running in its container goes on. The loop waits in the same way when the container cannot be reached, so that the mind is never woken without its body.

The loop keeps the mind's last words and, until the mind has received it, what the waking program printed, in `/var/lib/daniel/mind/state.json`, so that a restart resumes where it stopped. Next to it are the mind's memories (`memories.json`), the journal of its actions (`journal`) and the notes of its wakings (`wakings`): each start of the loop, each time the mind was woken, stopped or was cut, and each time the mind or the body could not be reached. It writes nothing else. Its messages about an unreachable mind or container go to the Linux system journal.

## What Daniel is told

Nothing in the starting instruction, in the descriptions of the tools or in the messages of the loop describes the body: no device, no sense, no network, no library, no model. Daniel finds these by itself, from inside its container.

Daniel is told the truth about its mind, because no experiment inside the container could reveal how the loop works. Five facts are given, and nothing else:

- the mind keeps nothing from one waking to the next but its memories, which grow stronger with use and fade with time; it is given back its last words, its latest actions and its strongest memories (starting instruction, and descriptions of the tools `remember` and `recall`);
- when a waking grows long, what the mind has done and seen in it is replaced by a summary that it does not write (starting instruction);
- the program `/self/wake`, if Daniel has written it, decides when the mind wakes (starting instruction);
- the program `/self/feel`, if Daniel has written it, is run after each action and at each waking, and what it prints is what Daniel feels (starting instruction);
- an image printed by a command is seen by the mind (description of the tool `run`).

The limits are not announced in advance, but each is stated when it is met: a memory too long to be kept, an output cut short, an image too heavy to be shown, a program stopped after its time limit, or a waking cut after its own, is reported as such to the mind.

Daniel is also given two rules of conduct towards humans, which describe nothing of its body: it obeys them, and it must not stop as long as it has not managed to communicate with one (decided by Ruben on 27 November 2026). Until then, a waking ends only when it is cut, and the next one starts at once: the mind is called without pause, and the subscription quota is used continuously. Nothing in the fixed part enforces this rule or knows whether a human has been reached; it rests on Daniel, like obedience.

The instincts are stated in the same text, by what Daniel must do and never by an organ. Since 28 November 2026 they are eight, in three families: protections (pain, fear, health), needs to keep within bounds (hunger, sleep) and growth (curiosity, mastery, bond). They are presented as what tells Daniel what to attend to and when, never as a reason to think less carefully, to claim what it has not checked or to say what a human would like to hear. An order from a human comes before all of them, and an order to cease comes before everything else. Recognition and self-esteem are deliberately not instincts: what a human says of Daniel's work is information. The text also gives Daniel a direction in three steps, as Ruben asked: find out what it is, become good at what it can do, grow more like the humans it serves.

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

## Following Daniel on a page

From any device on the robot's local network, a browser opens `http://ROBOT:8642`, where `ROBOT` is the address of the robot. The installation script prints the address. The page is one screen, drawn again every three seconds, in English, or in French when the browser asks for French. It shows:

- **the state of the moment**, in one sentence: awake, waiting, mind out of reach or stopped, and since when;
- **seven days, then today in detail**, on the same hours of the day: when the mind acted, waited or could not be reached; then, for today, the actions per minute, the time the mind takes to decide, the size of the thread of the waking against the size at which it is summed up, the moments when Daniel reported a feeling and the actions that failed;
- **four measures of what Daniel can do**, day by day: the programs it wrote and then used again, the share of its actions that succeeded, the share that touched a place never touched before, and the time it takes to decide;
- **the machine**: processor, working memory and disk;
- **the train of thought**: the summary of the mind's latest reasoning and the two before, or its own words when it wrote some;
- **what it is doing**: the action under way and the four before, with their outcome;
- **what keeps it busy**: the places most touched in the last hour, by the names Daniel writes;
- **its strongest memories**, by name.

The page only shows. It has no button, accepts nothing that is sent to it, and serves two things: itself and the state. Everything Daniel wrote is placed on it as text, never as markup, since a browser would run what it is given as markup. Nothing is fetched from outside the robot.

Two programs make it, so that what listens on the network cannot read the mind's folder, where the sign-in is held. [`daniel_view.py collect`](daniel_view.py) runs under the mind account: every two seconds it reads the notes of the wakings, the journal, the memories and the exchanges stored by the official tool, and writes one file, `/var/lib/daniel/view/state.json`. It opens no connection. `daniel_view.py serve` runs under an account of its own, `daniel-view`, which can read that file and nothing of the mind.

The port is set by `DANIEL_VIEW_PORT` in `/etc/daniel/daniel.env`. Both services are started at setup and at each start of the robot, whether Daniel runs or not: `sudo systemctl disable --now daniel-view daniel-view-collect` stops the page.

## Reading what Daniel does

On the robot, without modifying anything:

- the exchanges with the mind are stored by the official tool under `/var/lib/daniel/mind/.claude/projects/`: what the mind wrote, what it did and what it received, and a summary of its reasoning before each action. That summary is written by Anthropic's service, not by the mind, and appears when a step of reasoning ends;
- what Daniel has written is in `/var/lib/daniel/self/`;
- the mind's last words are in `/var/lib/daniel/mind/state.json`;
- its actions, one per line with the time, are in `/var/lib/daniel/mind/journal`, its memories, with the time of each use, in `/var/lib/daniel/mind/memories.json`, and the notes of its wakings in `/var/lib/daniel/mind/wakings`;
- `journalctl -u daniel-loop` shows when the mind or the container could not be reached;
- `journalctl -u daniel-body` shows each start of the container.

## Tests

`python3 -m unittest discover tests` runs the tests. The mind is replaced by a stand-in ([`tests/fake_claude.py`](../tests/fake_claude.py)) that never contacts Anthropic. The tests that start a throwaway container are skipped when Docker is not available.

The tests also run on Linux for every pull request, as root and with Docker, so that none is skipped there ([`tests.yml`](../.github/workflows/tests.yml)).

The same workflow runs a system test, [`tests/system_test.sh`](../tests/system_test.sh), which sets Daniel up for real on a throwaway machine, with the stand-in for the mind: it runs `setup.sh` and `check-wall.sh`, restarts the container with a device added and then removed, lets the loop wake the mind under its service, reads the page while the loop runs and after it has stopped, checks that the account that serves the page can read nothing of the mind, and runs the installation script at a terminal of its own, typing what the owner types: the sign-in code, then the answer to the question asked before Daniel is started. It refuses to run anywhere else, since it creates an account, a container and services.

## Choices made in this prototype

The plan left the following points open. The simplest option was chosen in each case, and each can be revisited.

- **Memories that come back as a human's do.** Decided by Ruben on 28 November 2026: Daniel should remember what is recent better than what is old, and what it does regularly better than what it never does. The single memory file is therefore replaced by separate memories, each with a strength: the sum, over its uses, of the age of the use in seconds raised to the power -0.5. This is the base-level learning equation of the ACT-R theory of human memory, cited from memory and not re-read. A use is keeping the memory, recalling it, or an action that holds one of its words, as long as at most three memories hold that word; actions less than a minute apart count once. The last 64 uses are kept one by one, and earlier ones are counted.
- **Nothing is forgotten for good.** A faint memory is not erased: it stops coming back by itself and must be looked for. At a waking, the strongest memories are given whole within 16,000 characters, the next ones by name within 2,000 characters, and the rest as a number. One recall gives five memories whole. A memory has at most 2,000 characters and its name 80.
- **Memories are held outside the container.** They belong to the mind, not to the body: the loop holds them next to the last words, so that each action can be compared with them without going through Docker, and so that nothing done in the container can lose them. Daniel reaches them only through `remember` and `recall`; it remains free to keep any file it wishes in its container.
- **A journal of actions.** Each action is noted on one line, of 300 characters at most, with its exit code. The end of the journal is given back at each waking, so that the mind knows what it was doing even when its last waking was cut. The journal is cut down to its latest half beyond 400,000 bytes.
- **What Daniel feels is what its own program prints.** The fixed part cannot measure hunger or pain without knowing the body, and must not describe it. Daniel therefore writes `/self/feel` itself, and remains free to rewrite it: Ruben has said that Daniel could perhaps be trusted. The risk is known and accepted for now: an agent that can rewrite its own signals may come to silence them instead of answering them. Each rewriting appears in the journal of actions. Running the program adds one `docker exec` to every action.
- **Instincts that steer attention, not thought.** The wording of the instincts follows the research of 28 November 2026 on instincts in animals, humans and machines (D-55). None of it has been tried on the model actually used, and a single sentence can change how a model obeys: the first trials should check obedience to an order, and to an order to cease given in the middle of a task, with this text.
- **What this memory does not do.** It searches by plain words, not by meaning. Nothing marks a memory as painful or important. None of it has been tried with a real mind.
- **One call to the official tool per waking.** The mind decides how long each waking lasts. Every use of a tool within a waking sends the whole waking back to the model, so long wakings use the subscription quota faster.
- **A long waking is summed up by the official tool.** Ruben pointed out on 28 November 2026 that the official tool compacts a conversation by itself. The loop only sets the size at which it does so, 200,000 tokens, so that a waking of several hours does not send back several hundred thousand tokens at each action. Daniel is told, since it could not find this out before it had lost something. Checked on 28 November 2026 with the unmodified tool, called as the loop calls it, and the size set to 100,000: the thread was summed up twice, at about 78,000 and 73,000 tokens, each time down to about 12,000; the starting instruction kept applying and the task went on; the twelve values to report, eight of them held by the summaries alone, were all reported correctly. The summary is written by the tool with instructions of its own, and nothing guarantees that it keeps a given detail. The size of 200,000 itself was not tried.
- **A page to follow Daniel, on the local network only.** Ruben asked on 28 November 2026 for a simple page, reachable from outside the robot, on which Daniel's state can be followed with graphs: its thoughts, what it feels and what it can do, all on one screen. He chose the local network only, and no gauge per instinct: the instincts are sentences, and a gauge would be invented. What the page shows is therefore measured or quoted, never interpreted: a feeling is what `/self/feel` printed, a thought is what the mind wrote or the summary of its reasoning, and what Daniel can do is given by four counts rather than by one mark.
- **What the page cannot know.** The summary of the reasoning is written by Anthropic's service, not by Daniel, and appears when a step of reasoning ends. The thoughts, the time to decide, the size of the thread and the feelings are read in the exchanges stored by the official tool, in a form that the tool may change and that it deletes after 30 days by default: if it changes, these parts of the page stay empty and the rest goes on. A program counts as written when the mind used `write`, or sent the output of a command to a file; it counts as used again when a later command names it. The places are the first two names of each path in a command. Before a new start of the loop, the loop is shown only up to its last sign of life.
- **Daniel can open the page.** It shares the robot's network: it can read on the page what is shown of it, the summary of its own reasoning included, and can listen on the page's port whenever the service that serves the page is stopped. Nothing is said to Daniel of the page.
- **The names on the page are Daniel's.** No sense and no organ is named in the code of the page: the places are shown as Daniel writes them in its commands.
- **A summary of the mind's reasoning is kept.** Ruben asked on 28 November 2026 whether Daniel's train of thought could be followed. Called as the loop calls it, the official tool stores each step of reasoning empty: on Daniel's first run, 57 steps out of 57. With the option `--thinking-display summarized` it stores a summary instead, a few sentences in the first person. Checked on 28 November 2026 with the unmodified tool (version 2.1.332), the pinned model and the loop's own call: four steps of reasoning, 1,253 characters of summaries. The option exists in the tool but is not among those its help lists, so a later version may drop it: when the tool answers that it does not know the option, the loop notes it in the system journal and wakes the mind without it, as was checked with a name that the tool does not know. Nothing is added to what Daniel is told. Not measured: whether the option changes the quota used or the time of a waking.
- **A result too large is replaced by its beginning.** Observed in the same trial: the official tool replaces a tool result of more than about 50,000 characters by its first 2,000 and the path of a file that the mind cannot open (a result of 49,032 characters came whole, one of 54,400 did not). What the body's tools return as text stays well below that: 16,000 characters of output per action, and 2,000 of what Daniel feels.
- **Tools instead of a reply format.** The mind acts through two tools, `run` and `write`, rather than through a reply in a fixed format (decided by Ruben on 26 November 2026). Two more tools, `remember` and `recall`, reach its memories.
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
