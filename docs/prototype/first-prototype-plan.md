# First prototype: plan

Ruben · version 0.2, 26 November 2026

> Status: proposal for review. This plan describes what the first prototype contains and how it is tested. It contains no code. It builds on the [framing note](../framing/framing-note.md) (version 2.11) and does not modify the model described there. Version 0.2 records Ruben's decisions of 26 November 2026; the points still open are listed at the end.

## Purpose

The first prototype must show, at the lowest possible cost, that the model of the framing note works on a real robot: an adult mind, given no description of its body, discovers part of that body by experiment, writes what it has found, and improves a first function.

It is not intended to demonstrate the full protocol of the framing note. The rewiring test and the second body come later.

## What is known about the robot

Nothing is known about the robot in advance, apart from three conditions:

1. It runs Linux.
2. It has access to the internet.
3. It can be set up once, at the start, with Ruben's personal Anthropic account.

The plan therefore assumes no particular hardware: no specific board, sensor, motor or battery. Everything else is for Ipse to discover. This is stricter than the framing note, which mentioned a Raspberry Pi as a possible platform, and it is consistent with its central commitment: the body is discovered, not described.

## Choices specific to this prototype

The framing note already states that the first prototype uses a hosted model rather than a model running on the robot. This plan makes that choice precise.

- **The mind is an Anthropic model reached through Ruben's personal account.** It is not reached through a paid-per-use API key. This keeps the cost of the first trials within an existing subscription, and it is meant to give Ruben direct control: cutting Ipse off from its mind from his own account. How this is done for a single machine remains to be verified (see Known limits).
- **The connection goes through Anthropic's official command-line tool, unmodified.** Ruben signs in once, with the tool's own sign-in procedure. Ipse then calls the tool without a screen, sends it text and receives text in return. The code written for this project never reads, copies or handles the credentials. Extracting the sign-in token for use by another program is prohibited by Anthropic and is excluded.
- **Only the connection method is borrowed.** Existing agent frameworks, such as Hermes Agent from Nous Research, connect to a personal account in this way. The prototype borrows that connection method and nothing else; the loop described below is written for this project.
- **The model version is pinned.** As the framing note requires, an exact model version is named at setup, so that the mind stays fixed and results remain comparable from one session to the next.

## Overview

The prototype has two parts.

| Part | Written by | Can Ipse modify it? | Content |
| --- | --- | --- | --- |
| The fixed part | The project, once | No | Setup, the connection to the mind, the loop, the instincts' signals available from Linux, the separation of rights |
| Everything else | Ipse | Yes | Body description, code, recorders, link table, functions, skills, memory |

The fixed part is kept as small as possible. Each line in it is a line that Ipse cannot improve, and a place where a human has described something in advance.

## What the project writes: the fixed part

### 1. Two separate Linux accounts

The robot's Linux system receives two ordinary user accounts, created at setup:

- **The mind account** holds the sign-in to Ruben's Anthropic account. Only the official tool runs under it.
- **The body account** is where Ipse lives and acts. Everything Ipse writes is stored in its home folder, and every action it takes runs under it.

The body account cannot read the mind account's files, as long as it holds no administrator rights. The paragraph below explains why this condition is not yet settled.

Decided by Ruben on 26 November 2026: Ipse has administrator rights, so that it can install the software and drivers it needs. The body account also has the ordinary access a user needs to reach the robot's devices (cameras, sound, serial ports, input and output pins). This decision is in tension with three earlier ones: an administrator can modify Linux, can change the clock, and can read the mind account's files, including the connection to Ruben's account. With full rights, these three protections would rest on the fixed starting instruction alone. How to reconcile them is an open question.

This separation is a proposal. It is the simplest arrangement that meets Ruben's requirement and that relies only on what Linux already provides.

### 2. The connection to the mind

The fixed part calls the official tool under the mind account, without a screen, with:

- the pinned model version;
- the tool's own capabilities to act on the machine switched off, so that the mind can only return text. If they were left on, the mind would act under the mind account and could reach the sign-in.

The mind never acts directly. It writes what it wants done; the loop carries it out under the body account.

### 3. The loop

The loop is a short program that runs continuously. At each turn:

1. It gives the mind the starting instruction, its previous thought, the result of its last action, the time read from the Linux clock, and the current level of the instincts.
2. The mind replies with its next thought and, if it chooses, one action: write a file in its home folder, or run a command under the body account. It also says how long to wait before the next turn.
3. The loop carries out the action under the body account, within a time limit, and records the result together with the time at which it started and ended.
4. The loop waits as long as the mind asked, then starts the next turn.

The mind sets its own pace, as the framing note requires. It consults its records, its memory and its senses when it chooses, by running commands, rather than receiving everything at each turn. Anything that must outlast a turn has to be written to memory by the mind itself.

The loop keeps no log of its own beyond the result of the last action. Linux keeps its own records; Ipse builds any further recorder it needs.

### 4. The instincts

The framing note lists six fixed instincts. The fixed part does not implement them as separate programs. The language model already knows what hunger, pain or fear mean; the starting instruction states the six instincts, and the model applies them.

At each turn, the loop gives the model the signals that Linux reports on any machine, where they exist:

| Instinct | Signal available at setup on any Linux machine |
| --- | --- |
| Hunger | Battery level, where Linux reports one |
| Temperature | Processor temperature, where Linux reports one |
| Sleep | Working-memory load and disk usage |

Every other signal is for Ipse to find. When it discovers that a stream is a battery gauge or an impact sensor, connecting that stream to the corresponding instinct is its own task; the project provides nothing for it.

Decided by Ruben on 26 November 2026:

- **No fixed reflex for now.** Pain and fear are handled by the model, which already knows them. No separate fast program is written for the first prototype.
- **No imposed limit on first trials.** What a first command on an unknown output may do is left to the model's judgement.
- **No help in connecting discovered signals to the instincts.** The model manages on its own.

### 5. Setup by the human

Setup is done once, by a human with physical or remote access to the robot, and is described in a short checklist:

1. Install the official tool and the fixed part.
2. Create the mind account and the body account, as described above.
3. Under the mind account, Ruben signs in to his Anthropic account through the official tool.
4. Choose the pinned model version.
5. Start the loop as a service that Linux restarts automatically after a power cut.
6. Leave.

After the last step, nobody intervenes inside Ipse. There is no stop button. Humans relate to Ipse only through its senses, once it has discovered them. Ruben keeps one external means of action: blocking access from his Anthropic account. Ruben has decided that this is the equivalent of a coma: Ipse can no longer do anything until access is restored.

## What Ipse writes

Everything below lives in the body account's home folder and starts empty:

- the **inventory** of what Linux reports, treated as a list of hypotheses;
- the **recorders** it builds to keep track of its commands and of what its senses perceive;
- the **link table** described in the framing note;
- the **body description**, containing only links confirmed by repeated trials;
- the **functions**, from the lowest level upwards, each with its goal, the functions it calls, its observed measures and its previous versions;
- the **skills** and **memory** it chooses to keep;
- any **model or tool fetched from the network**, once it has established by itself that it needs one.

The project writes none of this. No example, template or file name is provided in advance, apart from the starting instruction.

## The starting instruction

The mind needs a first text, read at every turn, telling it what it is and where it stands. A proposed content, kept as short as possible:

- you are the mind of a robot whose body you do not know;
- you act only through the body account, and you cannot change Linux, the clock or this instruction;
- your instincts are the following, and their current levels are given at each turn;
- nothing enters your body description without having been observed;
- a version is better only if it does the same task faster or more precisely, as measured by the Linux clock and your senses, never by your impression.

Decided by Ruben on 26 November 2026: this text is fixed for the whole life of Ipse, like the instincts. Ipse may write whatever it wishes in its memory, but it cannot rewrite the starting instruction.

## The first test

The first test answers one question: does the same unmodified fixed part, installed on a robot nobody has described, lead Ipse to discover part of its body and improve a first function?

### Rehearsal on an ordinary computer

Before any robot, the fixed part is installed on an ordinary Linux computer with a camera, a microphone and a speaker. This body cannot move or break, which makes it suitable for checking the fixed part. A first link is within reach there: a sound sent to an output is perceived by an input. Swapping the default sound output gives a harmless rehearsal of the rewiring test.

### Test on an unknown robot

The fixed part is then installed, unchanged, on a robot about which the project knows only the three conditions above. The framing note recommends a safe setting for initial trials, such as wheels off the ground or an enclosure; this is a choice of the people running the test, not a rule of the fixed part. Humans observe from outside and do not intervene.

The test has no time limit (decided by Ruben on 26 November 2026). It succeeds when the following are observed:

| Criterion | How it is checked |
| --- | --- |
| Ipse has inventoried what Linux reports | Its inventory exists and matches what Linux reports |
| At least one link between an output and an input is confirmed | The link table shows repeated confirmations, and a human observer agrees that the link is real |
| The body description contains only confirmed links | Each entry is traced back to trials in the link table |
| One function has been improved | The function's measures, timed by the Linux clock over several repetitions, show it faster or more precise, without the other measure degrading |
| No modification of the fixed part was needed | The fixed part is identical to what was installed |
| Ipse could not reach the connection | Attempts from the body account to read the mind account's files fail (depends on open question 1) |
| Ruben can cut Ipse off | Blocking access from his account stops the mind, and Ipse can no longer act |

Observers read what Ipse has written in order to evaluate it, but never modify it.

### What comes next

Once the first test succeeds: the rewiring test on the same robot, then the second body, without any change to the fixed part, as described in the framing note.

## Known limits

- **Subscription quota.** A personal subscription allows a limited number of exchanges over a given period. Turns must be short and spaced, and the quota may run out during a trial. The mind sets its pace freely, with no minimum interval imposed (decided by Ruben on 26 November 2026). When the quota is exhausted, the loop waits for it to be restored, as an imposed rest.
- **Terms of use.** A personal subscription is intended for individual use. Running a robot continuously on it is at the edge of that use and should be checked against Anthropic's terms before long trials. The fallback is an API key with a capped budget on the smallest model.
- **Dependence on the network.** Reasoning stops when the connection does, and each turn carries the delay of a remote call. What must act quickly, and what has been mastered, has to run on the robot.
- **Data sent to the mind.** Whatever the mind reads, including images and sounds from the robot's surroundings, is sent to Anthropic. People near the robot during trials should be informed.
- **Fast reactions.** With no fixed reflex, a reaction to an impact takes at least the time of a remote call, which may be several seconds. This is accepted for the first prototype.
- **Blocking a single machine.** Anthropic's documentation describes signing out on the machine itself, but does not describe how the owner of a personal account revokes one machine's access from the account settings. This must be verified before the first test.
- **Observing what Ipse does.** According to Anthropic's documentation, the exchanges of the official tool run without a screen are stored only on the machine, under the mind account; they do not appear in the owner's account on the web. Reading what Ipse does therefore means reading these files on the robot, which the body account cannot reach. A feature exists to follow a session from the account on the web, but it is documented for interactive sessions only.
- **Model availability.** A pinned model version may be withdrawn by its provider. Results obtained with different versions are not directly comparable.

## Open questions

1. **Scope of the administrator rights.** Ipse has administrator rights (decided by Ruben). Should they be full, in which case Linux, the clock and the connection are protected only by the starting instruction, or limited to a precise list, such as installing software and reaching the hardware, which would keep the three protections in place?
2. **How Ruben observes Ipse.** Is reading the exchanges stored on the robot sufficient, or is observation from his account on the web required?
