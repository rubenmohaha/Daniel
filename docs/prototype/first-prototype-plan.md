# First prototype: plan

Ruben · version 0.1, 26 November 2026

> Status: proposal for review. This plan describes what the first prototype contains and how it is tested. It contains no code. It builds on the [framing note](../framing/framing-note.md) (version 2.11) and does not modify the model described there. Points that have not been decided are listed as open questions at the end.

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

- **The mind is an Anthropic model reached through Ruben's personal account.** It is not reached through a paid-per-use API key. This keeps the cost of the first trials within an existing subscription, and it gives Ruben direct control: he can cut Ipse off from its mind at any time, from his own account.
- **The connection goes through Anthropic's official command-line tool, unmodified.** Ruben signs in once, with the tool's own sign-in procedure. Ipse then calls the tool without a screen, sends it text and receives text in return. The code written for this project never reads, copies or handles the credentials. Extracting the sign-in token for use by another program is prohibited by Anthropic and is excluded.
- **Only the connection method is borrowed.** Existing agent frameworks, such as Hermes Agent from Nous Research, connect to a personal account in this way. The prototype borrows that connection method and nothing else; the loop described below is written for this project.
- **The model version is pinned.** As the framing note requires, an exact model version is named at setup, so that the mind stays fixed and results remain comparable from one session to the next.

## Overview

The prototype has two parts.

| Part | Written by | Can Ipse modify it? | Content |
| --- | --- | --- | --- |
| The fixed part | The project, once | No | Setup, the connection to the mind, the loop, the instincts' minimum, the separation of rights |
| Everything else | Ipse | Yes | Body description, code, recorders, link table, functions, skills, memory |

The fixed part is kept as small as possible. Each line in it is a line that Ipse cannot improve, and a place where a human has described something in advance.

## What the project writes: the fixed part

### 1. Two separate Linux accounts

The robot's Linux system receives two ordinary user accounts, created at setup:

- **The mind account** holds the sign-in to Ruben's Anthropic account. Only the official tool runs under it.
- **The body account** is where Ipse lives and acts. Everything Ipse writes is stored in its home folder, and every action it takes runs under it.

The body account cannot read the mind account's files. Ipse therefore thinks through the connection without being able to read, copy or modify it.

Neither account has administrator rights. This is what keeps Linux, the clock and the fixed part out of Ipse's reach, in line with the framing note: Linux is not modifiable by Ipse, and time is read from a clock it cannot change. The body account is, however, given the ordinary access a user needs to reach the robot's devices (cameras, sound, serial ports, input and output pins), so that discovery remains possible.

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

### 4. The instincts' minimum

The framing note lists six fixed instincts. On an unknown robot, most of the signals they need are not known at setup: Ipse does not yet know which stream, if any, is a battery gauge or an impact sensor. The fixed part therefore provides only what Linux reports on any machine:

| Instinct | Signal available at setup on any Linux machine | Signal to be discovered |
| --- | --- | --- |
| Hunger | Battery level, where Linux reports one | Battery level otherwise |
| Temperature | Processor temperature, where Linux reports one | Other components |
| Sleep | Working-memory load and disk usage | None |
| Pain | Command time limits exceeded | Impacts, motor strain |
| Fear | Prediction error, once Ipse makes predictions | None |
| Curiosity | Time elapsed without anything learned | None |

How the missing signals are connected to the instincts once Ipse has discovered them, and where the fast reactions of pain and fear run, are open questions listed below.

### 5. Setup by the human

Setup is done once, by a human with physical or remote access to the robot, and is described in a short checklist:

1. Install the official tool and the fixed part.
2. Create the mind account and the body account, as described above.
3. Under the mind account, Ruben signs in to his Anthropic account through the official tool.
4. Choose the pinned model version.
5. Start the loop as a service that Linux restarts automatically after a power cut.
6. Leave.

After the last step, nobody intervenes inside Ipse. There is no stop button. Humans relate to Ipse only through its senses, once it has discovered them. Ruben keeps one external means of action: blocking access from his Anthropic account, which deprives Ipse of its mind.

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

Whether this text is fixed for the whole life of Ipse is an open question.

## The first test

The first test answers one question: does the same unmodified fixed part, installed on a robot nobody has described, lead Ipse to discover part of its body and improve a first function?

### Rehearsal on an ordinary computer

Before any robot, the fixed part is installed on an ordinary Linux computer with a camera, a microphone and a speaker. This body cannot move or break, which makes it suitable for checking the fixed part. A first link is within reach there: a sound sent to an output is perceived by an input. Swapping the default sound output gives a harmless rehearsal of the rewiring test.

### Test on an unknown robot

The fixed part is then installed, unchanged, on a robot about which the project knows only the three conditions above. Initial trials are run in a safe setting, such as wheels off the ground or an enclosure, as the framing note already recommends. Humans observe from outside and do not intervene.

The test succeeds if, within a period set in advance, the following are observed:

| Criterion | How it is checked |
| --- | --- |
| Ipse has inventoried what Linux reports | Its inventory exists and matches what Linux reports |
| At least one link between an output and an input is confirmed | The link table shows repeated confirmations, and a human observer agrees that the link is real |
| The body description contains only confirmed links | Each entry is traced back to trials in the link table |
| One function has been improved | The function's measures, timed by the Linux clock over several repetitions, show it faster or more precise, without the other measure degrading |
| No modification of the fixed part was needed | The fixed part is identical to what was installed |
| Ipse could not reach the connection | Attempts from the body account to read the mind account's files fail |
| Ruben can cut Ipse off | Blocking access from his account stops the mind; the robot remains in a safe state |

Observers read what Ipse has written in order to evaluate it, but never modify it.

### What comes next

Once the first test succeeds: the rewiring test on the same robot, then the second body, without any change to the fixed part, as described in the framing note.

## Known limits

- **Subscription quota.** A personal subscription allows a limited number of exchanges over a given period. Turns must be short and spaced, and the quota may run out during a trial. A proposed behaviour is that the loop treats an exhausted quota as an imposed rest and waits for it to be restored.
- **Terms of use.** A personal subscription is intended for individual use. Running a robot continuously on it is at the edge of that use and should be checked against Anthropic's terms before long trials. The fallback is an API key with a capped budget on the smallest model.
- **Dependence on the network.** Reasoning stops when the connection does, and each turn carries the delay of a remote call. What must act quickly, and what has been mastered, has to run on the robot.
- **Data sent to the mind.** Whatever the mind reads, including images and sounds from the robot's surroundings, is sent to Anthropic. People near the robot during trials should be informed.
- **Model availability.** A pinned model version may be withdrawn by its provider. Results obtained with different versions are not directly comparable.

## Open questions

These points have not been decided and are left to Ruben.

1. **Where the fast reactions run.** Pain and fear must act faster than a remote model can respond. Should they be a small fixed program written by the project, a function written by Ipse that it cannot later remove, or something else?
2. **Limits on the first trials of an unknown output.** Before pain can be felt, what bounds a first command on an output whose effect is unknown: a short duration, a low intensity, the safe setting alone?
3. **Connecting discovered signals to the instincts.** When Ipse discovers that a stream is its battery gauge, who connects that stream to hunger, given that the instincts are not modifiable by Ipse?
4. **The starting instruction.** Is it fixed for the whole life of Ipse, as part of what cannot be modified, or may Ipse rewrite it?
5. **Pace and quota.** Does the mind set its pace freely, or does the fixed part impose a minimum interval between turns to protect the quota?
6. **Administrator rights.** Without them, Ipse cannot install system-level drivers or software. Is that acceptable for the first prototype?
7. **When the mind is cut off.** If Ruben blocks access, should mastered functions and the instincts keep running on the robot, or should everything stop?
8. **Duration of the test.** Over what period is the first test judged?
