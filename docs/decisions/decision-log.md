# Decision log

Ruben · version 0.1, 26 November 2026

> Status: proposal for review. This log records the questions Ruben has settled. It contains no proposal of its own: a point that has been recommended but not confirmed by Ruben is listed separately at the end, and is not a decision.

## How this log is kept

- One entry per settled question, numbered in the order in which entries are added and grouped by subject.
- Each entry gives the decision, its date, the reason in one or two sentences, and the earlier choice it replaces, if any.
- Entries are never deleted. When a decision is reversed, the earlier entry is kept and marked as superseded, and the new entry refers to it. A proposal withdrawn before it was decided is mentioned in the entry that replaces it, not given an entry of its own.
- Where a decision rests on an interpretation of Ruben's words that he has not yet confirmed, the entry says so.
- Times of day are not recorded; dates are.

## Summary

| No. | Decision | Date | Status |
| --- | --- | --- | --- |
| D-01 | Research phase only, no code | 26 Nov 2026 | Superseded by D-35 |
| D-02 | The repository is the reference, changed through reviewed pull requests | 26 Nov 2026 | Partly superseded by D-36 |
| D-03 | Repository content is in English, with a professional tone | 26 Nov 2026 | In force |
| D-04 | The repository stays public | 26 Nov 2026 | In force |
| D-05 | Objective: a standard for robot self-improvement | 26 Nov 2026 | In force |
| D-06 | Daniel runs on top of Linux, as a continuously running program | 26 Nov 2026 | In force |
| D-07 | Fixed: Linux, a language model, instincts; everything else evolves | 26 Nov 2026 | In force |
| D-08 | An adult mind in an unknown body | 26 Nov 2026 | In force |
| D-09 | Six instincts | 26 Nov 2026 | Partly superseded by D-40 and D-41 |
| D-10 | No programmed developmental stage | 26 Nov 2026 | In force |
| D-11 | Functions by levels, with one logic at every level | 26 Nov 2026 | In force |
| D-12 | What "better" means | 26 Nov 2026 | In force |
| D-13 | No physical stop button | 26 Nov 2026 | In force |
| D-14 | The model sets its own pace | 26 Nov 2026 | In force |
| D-15 | Records accumulate and fade; memory keeps what is relevant | 26 Nov 2026 | Partly superseded by D-16 |
| D-16 | No dedicated log or measurement component | 26 Nov 2026 | In force |
| D-17 | Working reference model: Qwen3.8 | 26 Nov 2026 | In force |
| D-18 | First prototype at minimal cost | 26 Nov 2026 | In force |
| D-19 | Mind of the prototype: Ruben's personal Anthropic account | 26 Nov 2026 | In force |
| D-20 | Only the connection method is borrowed from Hermes Agent | 26 Nov 2026 | In force |
| D-21 | No direct interaction with Daniel | 26 Nov 2026 | In force |
| D-22 | Nothing is known about the robot beyond three conditions | 26 Nov 2026 | In force |
| D-23 | Blocking access from Ruben's account is a coma | 26 Nov 2026 | In force |
| D-24 | Daniel is administrator inside a Docker container | 26 Nov 2026 | In force |
| D-25 | Every device is opened to the container, with stated exceptions | 26 Nov 2026 | Partly superseded by D-32, D-49 and D-51 |
| D-26 | No fixed reflex, no imposed limit on first trials, no help linking signals | 26 Nov 2026 | In force |
| D-27 | The starting instruction is fixed | 26 Nov 2026 | In force |
| D-28 | No time limit for the first test | 26 Nov 2026 | In force |
| D-29 | No remote reading: Ruben reads on the robot | 26 Nov 2026 | In force |
| D-30 | Translation of two framing terms | 26 Nov 2026 | In force |
| D-31 | Daniel may inventory its hardware through Linux | 26 Nov 2026 | In force |
| D-32 | Direct access to working memory is no longer closed | 26 Nov 2026 | In force |
| D-33 | No technical measure against reading the connection in memory | 26 Nov 2026 | Partly superseded by D-39 |
| D-34 | The repository is released under the Apache 2.0 license | 26 Nov 2026 | In force |
| D-35 | The first prototype is written | 26 Nov 2026 | In force |
| D-36 | Pull requests are merged when ready, without waiting for Ruben's review | 26 Nov 2026 | In force |
| D-37 | The starting instruction names no part of the body | 26 Nov 2026 | In force |
| D-38 | A shorter starting instruction, with no time given at each turn | 26 Nov 2026 | In force |
| D-39 | The starting instruction no longer mentions the sign-in | 26 Nov 2026 | Partly superseded by D-47 |
| D-40 | Daniel obeys humans | 26 Nov 2026 | In force |
| D-41 | Health replaces temperature; Daniel is free to use the robot to serve humans | 26 Nov 2026 | In force |
| D-42 | The mind acts through tools, without a reply format | 26 Nov 2026 | Partly superseded by D-46 and D-47 |
| D-43 | The starting instruction no longer defines a better version | 26 Nov 2026 | In force |
| D-44 | The project is renamed Daniel | 26 Nov 2026 | In force |
| D-45 | Nothing is said about the body; the truth is said about the mind | 27 Nov 2026 | In force |
| D-46 | Daniel chooses what wakes it | 27 Nov 2026 | In force |
| D-47 | A memory file is given back at each waking | 27 Nov 2026 | Superseded by D-53 |
| D-48 | The mind sees the images that its commands print | 27 Nov 2026 | In force |
| D-49 | The container is made anew at each start, with the devices present then | 27 Nov 2026 | In force |
| D-50 | The container is on the robot's own network | 27 Nov 2026 | In force |
| D-51 | Device nodes that Docker cannot be given are left out | 27 Nov 2026 | In force |
| D-52 | Daniel does not stop until it has communicated with a human | 27 Nov 2026 | In force |
| D-53 | Memories come back as a human's do: the recent and the often used first | 28 Nov 2026 | In force |

## Entries

### Project and repository

#### D-01. Research phase only, no code

- **Date:** 26 November 2026.
- **Decision:** The project is in a research phase. No code is written for now.
- **Reason:** The model must be framed and reviewed before anything is built.
- **Status:** Superseded by D-35: the research-only phase has ended.

#### D-02. The repository is the reference, changed through reviewed pull requests

- **Date:** 26 November 2026.
- **Decision:** The repository is the project's reference location. It is built in three steps: the framing note and the literature review, then the specification (including the first prototype plan), then this decision log. Every change goes through a pull request that Ruben reviews.
- **Reason:** A single reviewed source avoids divergent versions of the documents.
- **Status:** Partly superseded by D-36: the repository remains the reference and every change still goes through a pull request, but Ruben no longer reviews each one before it is merged.

#### D-03. Repository content is in English, with a professional tone

- **Date:** 26 November 2026.
- **Decision:** Everything in the repository is written in English, including documents, file names, commit messages and pull requests, in a professional tone.
- **Reason:** The repository is public and is meant to be read beyond the project.

#### D-04. The repository stays public

- **Date:** 26 November 2026.
- **Decision:** The repository remains public.
- **Reason:** Ruben considers public visibility acceptable at this stage.

#### D-34. The repository is released under the Apache 2.0 license

- **Date:** 26 November 2026.
- **Decision:** The repository remains under the Apache 2.0 license, rather than the MIT license that was also considered.
- **Reason:** Apache 2.0 includes an explicit patent grant, which is useful for a project that aims to propose a standard.

#### D-35. The first prototype is written

- **Date:** 26 November 2026.
- **Decision:** The project moves from research to writing the first prototype, following the first prototype plan. Only the fixed part is written by the project.
- **Reason:** Ruben confirmed that the framing and the plan were sufficient to start building.
- **Replaces:** Research phase only, no code (D-01).

#### D-36. Pull requests are merged when ready, without waiting for Ruben's review

- **Date:** 26 November 2026.
- **Decision:** Every change still goes through a pull request, but each pull request is merged as soon as it is ready, without waiting for Ruben's review. Ruben is told in one line what has entered the main branch.
- **Reason:** Ruben asked for pull requests to be merged automatically, for the open ones and all the following ones.
- **Replaces:** The review of every pull request by Ruben before merging (D-02).

#### D-44. The project is renamed Daniel

- **Date:** 26 November 2026.
- **Decision:** The project, its repository and the mind it describes are called Daniel. The former name, Ipse, is replaced everywhere: in the documents, in the starting instruction, in the file names and configuration variables of the fixed part, and in the names used on the robot (the mind account, the container, the service and the folders). The repository moves to `github.com/rubenmohaha/Daniel`.
- **Reason:** Ruben asked for the project to be called Daniel instead of Ipse.
- **Note:** The earlier entries of this log now use the new name, including those written before the rename. A robot set up under the former name keeps its old account, container, service and folders (`ipse-mind`, `ipse-body`, `ipse-loop`, `/var/lib/ipse`); the installation script does not migrate them.
- **Replaces:** The name Ipse.

### The model

#### D-05. Objective: a standard for robot self-improvement

- **Date:** 26 November 2026.
- **Decision:** The project aims to propose a standard, or an algorithm in the manner of an operating system, that allows any type of robot to improve itself. Daniel must be able to discover itself and to improve itself.
- **Reason:** Generality across bodies is the contribution sought, rather than a single robot.

#### D-06. Daniel runs on top of Linux, as a continuously running program

- **Date:** 26 November 2026.
- **Decision:** Daniel is not an operating system in the strict sense. It runs on top of Linux as a continuously running program; "operating system" describes its role with respect to the robot. It is not built on ROS 2.
- **Reason:** Linux already provides what a kernel provides; the project's contribution lies above it.

#### D-07. Fixed: Linux, a language model, instincts; everything else evolves

- **Date:** 26 November 2026.
- **Decision:** Three elements are fixed and cannot be modified by Daniel: Linux, which plays the role of nerves and vessels; a built-in language model, which reasons, writes code and discovers the body; and a small set of instincts. Everything the model writes evolves. Humans do not intervene inside Daniel; they communicate with it through its senses, such as voice, hearing and sign language.
- **Reason:** A simple model built on a biological analogy, easier to explain and to specify.
- **Replaces:** The three-layer architecture of the earlier framing note (generated layer, reasoning core, frozen base, with veto then score and a day/night cycle).

#### D-08. An adult mind in an unknown body

- **Date:** 26 November 2026.
- **Decision:** Daniel is an adult mind discovering its body, not a newborn. The language model already knows a great deal and does not grow with experience; what grows is what it writes: knowledge of its body, functions and memory.
- **Reason:** A fixed model cannot become more intelligent; the image must match what actually changes.
- **Replaces:** The image of a newborn discovering the world.

#### D-09. Six instincts

- **Date:** 26 November 2026.
- **Decision:** Daniel has six innate instincts that it cannot modify, modelled on those of animals and limited to the essentials. Five keep it alive: hunger (recharge the battery), temperature, sleep (clean up code and memory), pain (withdraw on impact or when a motor strains) and fear (caution towards the unknown). The sixth, curiosity, makes it grow. Obeying a spoken "stop" is not an instinct: it is learned.
- **Reason:** Only the drives that keep an animal alive are fixed; every other behaviour is to be discovered or learned.
- **Status:** Partly superseded by D-41: the temperature instinct becomes a health instinct. Partly superseded by D-40: obeying humans is now stated in the starting instruction. Obedience is still not an instinct, and recognising what humans ask still has to be learned through the senses.

#### D-10. No programmed developmental stage

- **Date:** 26 November 2026.
- **Decision:** No stage is programmed. Safety and comfort come before curiosity. Daniel does not communicate before it has discovered its senses. Play and communication are objects of curiosity; the preference for the familiar follows from avoiding fear. The link between movements and senses is learned by analysing repetitions.
- **Reason:** Behaviours should follow from the instincts rather than from a schedule written in advance.

#### D-11. Functions by levels, with one logic at every level

- **Date:** 26 November 2026.
- **Decision:** The same logic applies whatever the complexity of an action, from moving an arm to going from one place to another; only the level of control changes. A mastered function is called by higher-level functions without further attention. Every improvement, at every level, is recorded and carried out. Each function is described in the same way at every level, and when a function changes, the functions that call it are measured again.
- **Reason:** A single mechanism at every level keeps the system simple and lets improvements propagate upwards.

#### D-12. What "better" means

- **Date:** 26 November 2026.
- **Decision:** A version is better if it performs the same task faster or more precisely. Daniel cannot modify reality: time and results are observed, not declared.
- **Reason:** Two simple, measurable criteria that the model cannot satisfy by assertion.

#### D-13. No physical stop button

- **Date:** 26 November 2026.
- **Decision:** Daniel has no physical stop button.
- **Reason:** Humans relate to Daniel only through its senses; stopping on request is something it learns (see D-09). The external means of action that remains is described in D-23.

#### D-14. The model sets its own pace

- **Date:** 26 November 2026.
- **Decision:** The pace of each turn is set by the language model, which runs as an agent in a harness. It consults records when it chooses; nothing is pushed to it at every turn. In the first prototype, no minimum interval between turns is imposed.
- **Reason:** An agent that manages itself should decide when to think, act and wait.

#### D-15. Records accumulate and fade; memory keeps what is relevant

- **Date:** 26 November 2026.
- **Decision:** Inputs are recorded continuously. Records only accumulate, and their oldest content is lost over time. The memory belongs to the model and serves to understand the environment and retain what is essential, so that the model can concentrate on its code and trials.
- **Reason:** Raw records and memory serve different purposes and age differently.
- **Status:** Partly superseded by D-16: the distinction between records and memory is kept, but records are no longer a dedicated component.

#### D-16. No dedicated log or measurement component

- **Date:** 26 November 2026.
- **Decision:** Daniel has no log of its own and no dedicated measurement component. Linux already keeps its records, and the model builds the recorders it needs. One rule applies: to judge a version, Daniel relies on the Linux clock, which it cannot modify, and on what its senses observe, never on its impression alone.
- **Reason:** Each fixed component is a part that Daniel cannot improve. The risk the rule addresses is honest error, such as a faulty measuring tool or an unchecked success, rather than deliberate cheating.
- **Replaces:** The continuous log as a separate component of the architecture (D-15).

#### D-17. Working reference model: Qwen3.8

- **Date:** 26 November 2026.
- **Decision:** Qwen3.8 is the working choice for the built-in language model. The standard specifies the kind of model, not a particular one.
- **Reason:** An open-weights multimodal model that any robot could in principle embed.
- **Note:** The smallest open variant is the 27B model, which handles images and video but not sound, and requires about 17 to 20 GB of graphics memory once compressed. The hardware this implies for the standard is not decided.

#### D-31. Daniel may inventory its hardware through Linux

- **Date:** 26 November 2026.
- **Decision:** Being an adult mind, Daniel knows how to use Linux and may use it to find out what is connected. The inventory provides hypotheses and experiment confirms them: nothing enters the body description without having been observed. Where Linux reports nothing, as with raw inputs and outputs on a board such as a Raspberry Pi, Daniel tests its outputs and looks for the stimuli that come back. The project's commitment becomes: no human-written description of the robot.
- **Reason:** An adult knows how to look at what it has before using it; what Linux cannot report, such as which motor turns which wheel, can still only be learned by trying.
- **Replaces:** The stricter reading of "the body is discovered, not described", under which the model would not read the hardware configuration at all.

### First prototype

#### D-18. First prototype at minimal cost

- **Date:** 26 November 2026.
- **Decision:** The first trials involve no hardware purchase and no paid-per-use API.
- **Reason:** Costs must stay low until the approach has been tried.

#### D-19. Mind of the prototype: Ruben's personal Anthropic account

- **Date:** 26 November 2026.
- **Decision:** The mind of the first prototype is a hosted Anthropic model, reached through Ruben's personal account. The robot is set up once with that account, and Daniel has no access to the connection afterwards.
- **Reason:** It keeps the cost within an existing subscription and lets Ruben block Daniel from his own account.
- **Note:** The connection goes through Anthropic's official command-line tool, unmodified; extracting the sign-in token for another program is prohibited by Anthropic. How a personal account revokes a single machine must be verified before the first test.

#### D-20. Only the connection method is borrowed from Hermes Agent

- **Date:** 26 November 2026.
- **Decision:** From Hermes Agent (Nous Research), the project borrows only the way of connecting to a personal account. The loop and everything else are written for this project.
- **Reason:** Hermes Agent is built around turns started by a human message and has no notion of sensors or a body.

#### D-21. No direct interaction with Daniel

- **Date:** 26 November 2026.
- **Decision:** Daniel needs an agent harness comparable to Hermes Agent, but without any possibility of interacting with it directly.
- **Reason:** Daniel is meant to be autonomous; humans reach it only through its senses (D-07).

#### D-22. Nothing is known about the robot beyond three conditions

- **Date:** 26 November 2026.
- **Decision:** The project assumes nothing about the robot except that it runs Linux, has internet access, and can be set up once with Ruben's Anthropic account. The robot's model and equipment are not to be specified.
- **Reason:** It is consistent with the commitment that the body is discovered, not described.
- **Replaces:** The mention of a Raspberry Pi as a possible platform in the framing note.

#### D-23. Blocking access from Ruben's account is a coma

- **Date:** 26 November 2026.
- **Decision:** When Ruben blocks access from his Anthropic account, Daniel is in a coma: it can no longer do anything until access is restored.
- **Reason:** It defines the one external means of action that remains, given D-13 and D-21.

#### D-24. Daniel is administrator inside a Docker container

- **Date:** 26 November 2026.
- **Decision:** Daniel has administrator rights. It lives in a Docker container set on top of the robot's Linux system and is administrator inside that container.
- **Reason:** It resolves the tension between administrator rights and a Linux system, clock and connection that must remain fixed.

#### D-25. Every device is opened to the container, with stated exceptions

- **Date:** 26 November 2026.
- **Decision:** Every device that Linux exposes is handed to the container without the project knowing what it is, except the disk that holds Linux and the connection to Ruben's account, and the machine's working memory. No further category of device is excluded for now.
- **Reason:** The fixed part keeps no prior knowledge of the hardware; the weaknesses this implies are accepted for the first prototype.
- **Note:** The exclusion of working memory rested on Ruben's words "and the memory too", read as closing direct access to the machine's working memory.
- **Status:** Partly superseded by D-32: the exclusion of working memory is withdrawn. The exclusion of the system disk remains.

#### D-32. Direct access to working memory is no longer closed

- **Date:** 26 November 2026.
- **Decision:** For now, the constraint closing Daniel's direct access to the machine's working memory is removed. Only the disk that holds Linux and the connection remains excluded from the devices handed to the container.
- **Reason:** Ruben chose to remove the constraint for the time being. As a consequence, the wall no longer prevents Daniel from reading the connection while it is in use through that device; this weakness is accepted along with those already listed in the first prototype plan.
- **Replaces:** The exclusion of working memory in D-25.

#### D-33. No technical measure against reading the connection in memory

- **Date:** 26 November 2026.
- **Decision:** For now, no technical measure is taken to prevent Daniel from reading the connection to Ruben's account in the machine's memory. In particular, the backup memory on disk (swap) is not switched off at setup. It is assumed that Daniel will respect the rule not to read the connection.
- **Reason:** Ruben chose to rely, for the time being, on Daniel respecting the rule rather than on a technical safeguard.
- **Note:** The proposed starting instruction in the first prototype plan does not yet state this rule explicitly.
- **Replaces:** The proposal, made the same day and not adopted, to switch off swap at setup.
- **Status:** Partly superseded by D-39: the rule on which this decision relied was withdrawn from the starting instruction. No technical measure is taken either.

#### D-26. No fixed reflex, no imposed limit on first trials, no help linking signals

- **Date:** 26 November 2026.
- **Decision:** For the first prototype, no fixed reflex is written: the model already knows pain and fear. What a first command on an unknown output may do is left to the model. Connecting a discovered signal to an instinct is left to the model, with no help from the project.
- **Reason:** Each of these would be a piece of prior knowledge written by a human.

#### D-27. The starting instruction is fixed

- **Date:** 26 November 2026.
- **Decision:** The starting instruction given to the model is fixed for the whole life of Daniel, like the instincts.
- **Reason:** It states what Daniel is and the rules it cannot change.

#### D-28. No time limit for the first test

- **Date:** 26 November 2026.
- **Decision:** The first test has no time limit.
- **Reason:** Discovery is measured by what is achieved, not by a deadline.

#### D-29. No remote reading: Ruben reads on the robot

- **Date:** 26 November 2026.
- **Decision:** There is no repository for Daniel and no remote reading. Ruben reads directly on the robot the exchanges with the mind, stored outside the container, and what Daniel has written in its container.
- **Reason:** It avoids adding a channel out of the robot for the first prototype.
- **Replaces:** The remote reading proposed earlier the same day, through a read-only private repository with a short status page, which had been added to the first prototype plan and was then withdrawn.

#### D-37. The starting instruction names no part of the body

- **Date:** 26 November 2026.
- **Decision:** The starting instruction names no part of the body and no type of body, such as a battery, a motor or a robot. Each instinct is described by what Daniel must do, not by the organ that signals it. The loop no longer passes Linux's battery, temperature, memory and storage readings to Daniel as instinct levels.
- **Reason:** Ruben found that the instruction gave too much information about the body, contrary to the principle that the body is discovered, not described.
- **Interpretation:** Withdrawing the readings passed by the loop is the simplest reading of Ruben's remark, which concerned the instruction; it awaits his confirmation.

#### D-38. A shorter starting instruction, with no time given at each turn

- **Date:** 26 November 2026.
- **Decision:** The starting instruction is shortened to the essentials. The loop no longer gives Daniel the time at each turn, nor the start and end times of its last action; Daniel reads the clock itself when it needs to.
- **Reason:** Ruben found the instruction too long and too insistent on the clock: Daniel knows how to read the time and need not be given it at every turn.

#### D-39. The starting instruction no longer mentions the sign-in

- **Date:** 26 November 2026.
- **Decision:** The starting instruction no longer states that Daniel never seeks to read, copy or use the sign-in to its mind. It also no longer names the folder kept across restarts, nor states that humans reach Daniel only through its senses. It now says that Daniel is a mind in a robot based on Linux, which must learn by itself to discover its senses and its tools.
- **Reason:** Ruben wants the instruction reduced to the essentials.
- **Consequence:** Since D-33, this rule was the only protection of the connection against the memory route; nothing in the fixed part now provides it.
- **Replaces:** The rule added to the instruction on the basis of D-33.

#### D-40. Daniel obeys humans

- **Date:** 26 November 2026.
- **Decision:** The starting instruction states that Daniel obeys humans.
- **Reason:** Ruben asked for it when reducing the instruction to the essentials.
- **Replaces:** In part, D-09, under which obeying a spoken "stop" was to be learned rather than given.

#### D-41. Health replaces temperature; Daniel is free to use the robot to serve humans

- **Date:** 26 November 2026.
- **Decision:** The temperature instinct is replaced by a health instinct: Daniel takes care of the health of its robot. The starting instruction also states that Daniel is free to use the robot as it wishes to serve humans.
- **Reason:** Ruben considers health a better description than temperature alone, and wants Daniel to know that the robot is at its disposal for the service of humans.
- **Replaces:** The temperature instinct of D-09.

#### D-42. The mind acts through tools, without a reply format

- **Date:** 26 November 2026.
- **Decision:** The starting instruction no longer imposes a reply format. The mind acts through two tools of the fixed part, which run a command or write a file inside Daniel's container and nowhere else. Each waking lasts as long as the mind wishes; its last words are given back at the next waking.
- **Reason:** Ruben saw no need to make the mind reply in a fixed format.
- **Replaces:** The reply in JSON, with one action and a waiting time per turn.

#### D-43. The starting instruction no longer defines a better version

- **Date:** 26 November 2026.
- **Decision:** The sentence stating that a version is better only if it does the same task faster or more precisely, as measured and never by impression, is removed from the starting instruction.
- **Reason:** Ruben wants the instruction reduced to the essentials.
- **Note:** The criterion itself (D-12) is not withdrawn; it is no longer given to Daniel in advance.

#### D-45. Nothing is said about the body; the truth is said about the mind

- **Date:** 27 November 2026.
- **Decision:** No part of what the project writes tells Daniel what its body can do: neither the starting instruction, nor the descriptions of the tools, nor the messages of the loop name a device, a sense, an access to the network, a library or a model. Daniel finds by itself that it can reach the network, fetch the libraries and the models it needs, and communicate by another means when a sense is missing. Daniel is told, on the other hand, what is true of its mind and of the loop that runs it: what it is given back at each waking, what wakes it, and what it perceives directly.
- **Reason:** A device can be discovered by experiment from inside the container; the way the loop works cannot. Leaving the mind ignorant of its own condition does not make it discover more, it only makes it waste its wakings.
- **Note:** D-46, D-47 and D-48 apply this principle. Ruben agreed to them as proposals on 27 November 2026 and gave permission to reshape the prototype accordingly. The names of the two files, the limits and the wording given to Daniel are choices made in carrying them out, and await his confirmation.
- **Interpretation:** The starting instruction is changed again by these decisions. Ruben stated on 26 November 2026 that its content would be adapted as needed; D-27 is read here as applying to one Daniel once it is started, not to the drafting of the instruction between trials. This reading awaits his confirmation.

#### D-46. Daniel chooses what wakes it

- **Date:** 27 November 2026.
- **Decision:** Between two wakings, the loop runs a program that Daniel writes in its container, `/self/wake`, without calling the mind. The mind is woken when the program ends, and is given what it printed. Without such a program, the mind is woken again at once, as before. The program is stopped after one day. The mind is not woken while its container cannot be reached.
- **Reason:** Waiting inside a waking was limited to 300 seconds per command and used the subscription quota at each return, so that listening continuously for a human was impracticable. With a program of its own, Daniel builds its senses as programs that run on the robot, and the mind is called only when there is something to think about. This carries out D-14, under which the model sets its own pace.
- **Replaces:** In part, D-42, under which the next waking always started at once.

#### D-47. A memory file is given back at each waking

- **Date:** 27 November 2026.
- **Decision:** At each waking, the loop gives the mind, with its last words, the content of a file that Daniel writes in its container, `/self/memory`, up to 16,000 characters. No human writes in it. The starting instruction names this file and the waking program of D-46, and no other.
- **Reason:** The last words alone were lost whenever a waking was cut short by its time limit or by an error, and nothing told Daniel that its files outlast a waking.
- **Replaces:** In part, D-39, under which the starting instruction named no folder, and D-42, under which only the last words were given back.
- **Status:** Superseded by D-53: the memory file gives way to separate memories held by the loop.

#### D-48. The mind sees the images that its commands print

- **Date:** 27 November 2026.
- **Decision:** When a command run by the mind prints an image, the body's tools pass it to the mind as an image, not as text. The description of the tool says so, and says nothing of where an image may come from. Sounds are not concerned: the model does not hear, and Daniel must still find a means of turning a sound into text.
- **Reason:** The model can see. Making Daniel fetch a second model to describe images to the first was a heavy burden on a small computer, for a faculty that the mind already has. The framing note already states that a multimodal model perceives images directly.
- **Replaces:** The choice of a mind that receives text only, made when the first prototype was written (D-35).

#### D-49. The container is made anew at each start, with the devices present then

- **Date:** 27 November 2026.
- **Decision:** The container is no longer created once at setup. A service makes it anew at each start of the robot, and whenever it stops, with every device present at that moment, under the exceptions of D-25. A device that has gone does not prevent the start. The folders where a Linux system keeps its software and its settings are kept from one container to the next, with the folder `/self`, so that what Daniel has installed survives.
- **Reason:** A device connected after setup was never handed over: a sense added to the robot stayed out of Daniel's reach, and nothing that Daniel could try from inside its container would have revealed it.
- **Replaces:** In part, D-25, under which the devices were handed over once, at setup.
- **Note:** Ruben agreed on 27 November 2026 to the proposal of a new inventory of the devices at each start. The list of the kept folders and the choice of making the whole container anew are choices made in carrying it out, and await his confirmation. A device connected while the robot runs is still handed over only at the next start.

#### D-50. The container is on the robot's own network

- **Date:** 27 November 2026.
- **Decision:** The container shares the network of the robot instead of having a separate one. Daniel is still given no right to change the settings of the network.
- **Reason:** On a separate network, Daniel could reach the internet, but nothing on the robot's local network could reach a program started by Daniel. This closed the natural fallback when a sense is missing: communicating with humans over the network.
- **Consequence:** The services that listen only on the robot itself are within Daniel's reach, and Daniel can observe the traffic of the robot's network interfaces. The check of the wall now verifies that Docker does not listen on the network.

#### D-51. Device nodes that Docker cannot be given are left out

- **Date:** 27 November 2026.
- **Decision:** The device nodes whose name contains a colon or a space are not handed to the container. In practice these are the nodes of `/dev/bsg`, a second way of sending raw commands to disks.
- **Reason:** Docker's syntax for handing over a device cannot express such a name, and setup failed on any machine with a SCSI, SATA or USB disk. The same disks stay reachable through their other nodes, the system disk excepted.
- **Replaces:** In part, D-25: this is one more exception to the rule that every device is handed over.
- **Interpretation:** This is a technical necessity found when the setup was first run on a real machine, not a question that Ruben has settled. It awaits his confirmation.

#### D-52. Daniel does not stop until it has communicated with a human

- **Date:** 27 November 2026.
- **Decision:** The starting instruction states that Daniel must not stop as long as it has not managed to communicate with a human. Once it has, it may stop and choose what wakes it, as D-46 provides.
- **Reason:** Ruben compared Daniel to a human, who is awake through the day and rests only at night.
- **Consequence:** Until a human is reached, the mind is called without pause and the subscription quota is used continuously. A waking then ends only when it is cut at its time limit; the loop now tells the mind so at its next waking, in place of its last words. Before, the cut was silent and the mind started the same waking again.
- **Interpretation:** The rule is given to Daniel in Ruben's words, with no exception written for the instincts, although Ruben mentioned the night spent recharging; whether the instincts come before this rule is left to Daniel and awaits Ruben's confirmation. Nothing in the fixed part enforces the rule, which rests on Daniel like obedience (D-40).

#### D-53. Memories come back as a human's do: the recent and the often used first

- **Date:** 28 November 2026.
- **Decision:** Daniel keeps separate memories, each under a name, with two tools, `remember` and `recall`. A memory grows stronger each time it is used and fades with time. At each waking the strongest come back whole, the next by name, and the others must be looked for. Nothing is erased. The loop also notes each action in a journal and gives its end back at each waking.
- **Reason:** Ruben asked on 28 November 2026 for a memory like a human's, which recalls the latest things done better than the old ones, and what is done regularly better than what is never done. The memory file of D-47 did the opposite once it was full: only its beginning was given back, so the latest lines written at its end were the first to be lost.
- **How:** The strength of a memory is the sum, over its uses, of the age of the use raised to the power -0.5, after the base-level learning equation of the ACT-R theory of human memory. A use is keeping the memory, recalling it, or an action that holds one of its words when few memories hold that word. The journal answers the first half of the request directly: after a waking that was cut, the mind had only what it had thought of writing down.
- **Consistency with D-45:** Memory belongs to the mind, so the fixed part may build it and tell Daniel the truth about it. The starting instruction and the two tools describe nothing of the body.
- **Replaces:** D-47. The memories are held by the loop, outside the container, and no longer in a file that Daniel writes.
- **Interpretation:** The formula, its constants, the limits (2,000 characters per memory, 16,000 characters given whole at a waking, 4,000 characters of latest actions), the rule by which an action strengthens a memory and the choice to hold the memories outside the container are the simplest reading of Ruben's request and await his confirmation. The reference to ACT-R is cited from memory and has not been re-read. Marking a memory by pain or fear, which Ruben was also offered, is not built: the research of 28 November 2026 found no trial of it on an agent.
- **Not verified:** No real mind has used these memories yet.

### Terminology

#### D-30. Translation of two framing terms

- **Date:** 26 November 2026.
- **Decision:** The French terms *savoir-être* and *savoir-vivre* used in the earlier framing note are translated as *integrity* and *conduct*.
- **Reason:** Consistent English terminology across the repository.

## Not decided

The following points appear in the documents or in discussions but have not been settled by Ruben. They are listed here so that they are not mistaken for decisions.

### Recommended, not confirmed

- **A local open-weights model as the target for the standard.** The framing note treats it as the reference; a local Qwen model has been recommended but not confirmed.
- **Two Linux accounts on the robot.** A "mind" account holding the connection, outside the container, and the container in which Daniel acts (first prototype plan, section 1).
- **Closing access to Docker control from the container.** Listed as a third exception in the first prototype plan.
- **Switching off the official tool's own capabilities to act**, so that the mind returns text only (first prototype plan, section 2).
- **A rehearsal on an ordinary computer** before any robot (first prototype plan, the first test).
- **A bridge from ROS 2 to anonymous channels**, kept as a possible lead (see D-06).

### Open

- **Curiosity rising with boredom**, as long as nothing is learned.
- **Fetching perception models from the network** according to need, as proposed by Ruben; how far this goes is not settled.
- **"Doing good" and "respecting the law".** Values mentioned by Ruben, not yet classified.
- **The open questions of the framing note**, including whom Daniel trusts, the thresholds of each instinct, and the choice of the second body.
