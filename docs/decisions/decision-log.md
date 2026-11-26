# Decision log

Ruben · version 0.1, 26 November 2026

> Status: proposal for review. This log records the questions Ruben has settled. It contains no proposal of its own: a point that has been recommended but not confirmed by Ruben is listed separately at the end, and is not a decision.

## How this log is kept

- One entry per settled question, numbered in the order in which entries are added.
- Each entry gives the decision, its date, the reason in one or two sentences, and the earlier choice it replaces, if any.
- Entries are never deleted. When a decision is reversed, the earlier entry is kept and marked as superseded, and the new entry refers to it. A proposal withdrawn before it was decided is mentioned in the entry that replaces it, not given an entry of its own.
- Where a decision rests on an interpretation of Ruben's words that he has not yet confirmed, the entry says so.
- Times of day are not recorded; dates are.

## Summary

| No. | Decision | Date | Status |
| --- | --- | --- | --- |
| D-01 | Research phase only, no code | 26 Nov 2026 | In force |
| D-02 | The repository is the reference, changed through reviewed pull requests | 26 Nov 2026 | In force |
| D-03 | Repository content is in English, with a professional tone | 26 Nov 2026 | In force |
| D-04 | The repository stays public | 26 Nov 2026 | In force |
| D-05 | Objective: a standard for robot self-improvement | 26 Nov 2026 | In force |
| D-06 | Ipse runs on top of Linux, as a continuously running program | 26 Nov 2026 | In force |
| D-07 | Fixed: Linux, a language model, instincts; everything else evolves | 26 Nov 2026 | In force |
| D-08 | An adult mind in an unknown body | 26 Nov 2026 | In force |
| D-09 | Six instincts | 26 Nov 2026 | In force |
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
| D-21 | No direct interaction with Ipse | 26 Nov 2026 | In force |
| D-22 | Nothing is known about the robot beyond three conditions | 26 Nov 2026 | In force |
| D-23 | Blocking access from Ruben's account is a coma | 26 Nov 2026 | In force |
| D-24 | Ipse is administrator inside a Docker container | 26 Nov 2026 | In force |
| D-25 | Every device is opened to the container, with stated exceptions | 26 Nov 2026 | In force |
| D-26 | No fixed reflex, no imposed limit on first trials, no help linking signals | 26 Nov 2026 | In force |
| D-27 | The starting instruction is fixed | 26 Nov 2026 | In force |
| D-28 | No time limit for the first test | 26 Nov 2026 | In force |
| D-29 | No remote reading: Ruben reads on the robot | 26 Nov 2026 | In force |
| D-30 | Translation of two framing terms | 26 Nov 2026 | In force |

## Entries

### Project and repository

#### D-01. Research phase only, no code

- **Date:** 26 November 2026.
- **Decision:** The project is in a research phase. No code is written for now.
- **Reason:** The model must be framed and reviewed before anything is built.

#### D-02. The repository is the reference, changed through reviewed pull requests

- **Date:** 26 November 2026.
- **Decision:** The repository is the project's reference location. It is built in three steps: the framing note and the literature review, then the specification (including the first prototype plan), then this decision log. Every change goes through a pull request that Ruben reviews.
- **Reason:** A single reviewed source avoids divergent versions of the documents.

#### D-03. Repository content is in English, with a professional tone

- **Date:** 26 November 2026.
- **Decision:** Everything in the repository is written in English, including documents, file names, commit messages and pull requests, in a professional tone.
- **Reason:** The repository is public and is meant to be read beyond the project.

#### D-04. The repository stays public

- **Date:** 26 November 2026.
- **Decision:** The repository remains public.
- **Reason:** Ruben considers public visibility acceptable at this stage.

### The model

#### D-05. Objective: a standard for robot self-improvement

- **Date:** 26 November 2026.
- **Decision:** The project aims to propose a standard, or an algorithm in the manner of an operating system, that allows any type of robot to improve itself. Ipse must be able to discover itself and to improve itself.
- **Reason:** Generality across bodies is the contribution sought, rather than a single robot.

#### D-06. Ipse runs on top of Linux, as a continuously running program

- **Date:** 26 November 2026.
- **Decision:** Ipse is not an operating system in the strict sense. It runs on top of Linux as a continuously running program; "operating system" describes its role with respect to the robot. It is not built on ROS 2.
- **Reason:** Linux already provides what a kernel provides; the project's contribution lies above it.

#### D-07. Fixed: Linux, a language model, instincts; everything else evolves

- **Date:** 26 November 2026.
- **Decision:** Three elements are fixed and cannot be modified by Ipse: Linux, which plays the role of nerves and vessels; a built-in language model, which reasons, writes code and discovers the body; and a small set of instincts. Everything the model writes evolves. Humans do not intervene inside Ipse; they communicate with it through its senses, such as voice, hearing and sign language.
- **Reason:** A simple model built on a biological analogy, easier to explain and to specify.
- **Replaces:** The three-layer architecture of the earlier framing note (generated layer, reasoning core, frozen base, with veto then score and a day/night cycle).

#### D-08. An adult mind in an unknown body

- **Date:** 26 November 2026.
- **Decision:** Ipse is an adult mind discovering its body, not a newborn. The language model already knows a great deal and does not grow with experience; what grows is what it writes: knowledge of its body, functions and memory.
- **Reason:** A fixed model cannot become more intelligent; the image must match what actually changes.
- **Replaces:** The image of a newborn discovering the world.

#### D-09. Six instincts

- **Date:** 26 November 2026.
- **Decision:** Ipse has six innate instincts that it cannot modify, modelled on those of animals and limited to the essentials. Five keep it alive: hunger (recharge the battery), temperature, sleep (clean up code and memory), pain (withdraw on impact or when a motor strains) and fear (caution towards the unknown). The sixth, curiosity, makes it grow. Obeying a spoken "stop" is not an instinct: it is learned.
- **Reason:** Only the drives that keep an animal alive are fixed; every other behaviour is to be discovered or learned.

#### D-10. No programmed developmental stage

- **Date:** 26 November 2026.
- **Decision:** No stage is programmed. Safety and comfort come before curiosity. Ipse does not communicate before it has discovered its senses. Play and communication are objects of curiosity; the preference for the familiar follows from avoiding fear. The link between movements and senses is learned by analysing repetitions.
- **Reason:** Behaviours should follow from the instincts rather than from a schedule written in advance.

#### D-11. Functions by levels, with one logic at every level

- **Date:** 26 November 2026.
- **Decision:** The same logic applies whatever the complexity of an action, from moving an arm to going from one place to another; only the level of control changes. A mastered function is called by higher-level functions without further attention. Every improvement, at every level, is recorded and carried out. Each function is described in the same way at every level, and when a function changes, the functions that call it are measured again.
- **Reason:** A single mechanism at every level keeps the system simple and lets improvements propagate upwards.

#### D-12. What "better" means

- **Date:** 26 November 2026.
- **Decision:** A version is better if it performs the same task faster or more precisely. Ipse cannot modify reality: time and results are observed, not declared.
- **Reason:** Two simple, measurable criteria that the model cannot satisfy by assertion.

#### D-13. No physical stop button

- **Date:** 26 November 2026.
- **Decision:** Ipse has no physical stop button.
- **Reason:** Humans relate to Ipse only through its senses; stopping on request is something it learns (see D-09). The external means of action that remains is described in D-23.

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
- **Decision:** Ipse has no log of its own and no dedicated measurement component. Linux already keeps its records, and the model builds the recorders it needs. One rule applies: to judge a version, Ipse relies on the Linux clock, which it cannot modify, and on what its senses observe, never on its impression alone.
- **Reason:** Each fixed component is a part that Ipse cannot improve. The risk the rule addresses is honest error, such as a faulty measuring tool or an unchecked success, rather than deliberate cheating.
- **Replaces:** The continuous log as a separate component of the architecture (D-15).

#### D-17. Working reference model: Qwen3.8

- **Date:** 26 November 2026.
- **Decision:** Qwen3.8 is the working choice for the built-in language model. The standard specifies the kind of model, not a particular one.
- **Reason:** An open-weights multimodal model that any robot could in principle embed.
- **Note:** The smallest open variant is the 27B model, which handles images and video but not sound, and requires about 17 to 20 GB of graphics memory once compressed. The hardware this implies for the standard is not decided.

### First prototype

#### D-18. First prototype at minimal cost

- **Date:** 26 November 2026.
- **Decision:** The first trials involve no hardware purchase and no paid-per-use API.
- **Reason:** Costs must stay low until the approach has been tried.

#### D-19. Mind of the prototype: Ruben's personal Anthropic account

- **Date:** 26 November 2026.
- **Decision:** The mind of the first prototype is a hosted Anthropic model, reached through Ruben's personal account. The robot is set up once with that account, and Ipse has no access to the connection afterwards.
- **Reason:** It keeps the cost within an existing subscription and lets Ruben block Ipse from his own account.
- **Note:** The connection goes through Anthropic's official command-line tool, unmodified; extracting the sign-in token for another program is prohibited by Anthropic. How a personal account revokes a single machine must be verified before the first test.

#### D-20. Only the connection method is borrowed from Hermes Agent

- **Date:** 26 November 2026.
- **Decision:** From Hermes Agent (Nous Research), the project borrows only the way of connecting to a personal account. The loop and everything else are written for this project.
- **Reason:** Hermes Agent is built around turns started by a human message and has no notion of sensors or a body.

#### D-21. No direct interaction with Ipse

- **Date:** 26 November 2026.
- **Decision:** Ipse needs an agent harness comparable to Hermes Agent, but without any possibility of interacting with it directly.
- **Reason:** Ipse is meant to be autonomous; humans reach it only through its senses (D-07).

#### D-22. Nothing is known about the robot beyond three conditions

- **Date:** 26 November 2026.
- **Decision:** The project assumes nothing about the robot except that it runs Linux, has internet access, and can be set up once with Ruben's Anthropic account. The robot's model and equipment are not to be specified.
- **Reason:** It is consistent with the commitment that the body is discovered, not described.
- **Replaces:** The mention of a Raspberry Pi as a possible platform in the framing note.

#### D-23. Blocking access from Ruben's account is a coma

- **Date:** 26 November 2026.
- **Decision:** When Ruben blocks access from his Anthropic account, Ipse is in a coma: it can no longer do anything until access is restored.
- **Reason:** It defines the one external means of action that remains, given D-13 and D-21.

#### D-24. Ipse is administrator inside a Docker container

- **Date:** 26 November 2026.
- **Decision:** Ipse has administrator rights. It lives in a Docker container set on top of the robot's Linux system and is administrator inside that container.
- **Reason:** It resolves the tension between administrator rights and a Linux system, clock and connection that must remain fixed.

#### D-25. Every device is opened to the container, with stated exceptions

- **Date:** 26 November 2026.
- **Decision:** Every device that Linux exposes is handed to the container without the project knowing what it is, except the disk that holds Linux and the connection to Ruben's account, and the machine's working memory. No further category of device is excluded for now.
- **Reason:** The fixed part keeps no prior knowledge of the hardware; the weaknesses this implies are accepted for the first prototype.
- **Note:** The exclusion of working memory rests on Ruben's words "and the memory too", read as closing direct access to the machine's working memory. This reading is to be confirmed.

#### D-26. No fixed reflex, no imposed limit on first trials, no help linking signals

- **Date:** 26 November 2026.
- **Decision:** For the first prototype, no fixed reflex is written: the model already knows pain and fear. What a first command on an unknown output may do is left to the model. Connecting a discovered signal to an instinct is left to the model, with no help from the project.
- **Reason:** Each of these would be a piece of prior knowledge written by a human.

#### D-27. The starting instruction is fixed

- **Date:** 26 November 2026.
- **Decision:** The starting instruction given to the model is fixed for the whole life of Ipse, like the instincts.
- **Reason:** It states what Ipse is and the rules it cannot change.

#### D-28. No time limit for the first test

- **Date:** 26 November 2026.
- **Decision:** The first test has no time limit.
- **Reason:** Discovery is measured by what is achieved, not by a deadline.

#### D-29. No remote reading: Ruben reads on the robot

- **Date:** 26 November 2026.
- **Decision:** There is no repository for Ipse and no remote reading. Ruben reads directly on the robot the exchanges with the mind, stored outside the container, and what Ipse has written in its container.
- **Reason:** It avoids adding a channel out of the robot for the first prototype.
- **Replaces:** The remote reading proposed earlier the same day, through a read-only private repository with a short status page, which had been added to the first prototype plan and was then withdrawn.

### Terminology

#### D-30. Translation of two framing terms

- **Date:** 26 November 2026.
- **Decision:** The French terms *savoir-être* and *savoir-vivre* used in the earlier framing note are translated as *integrity* and *conduct*.
- **Reason:** Consistent English terminology across the repository.

## Not decided

The following points appear in the documents or in discussions but have not been settled by Ruben. They are listed here so that they are not mistaken for decisions.

### Recommended, not confirmed

- **A local open-weights model as the target for the standard.** The framing note treats it as the reference; a local Qwen model has been recommended but not confirmed.
- **Two Linux accounts on the robot.** A "mind" account holding the connection, outside the container, and the container in which Ipse acts (first prototype plan, section 1).
- **Closing access to Docker control from the container.** Listed as a third exception in the first prototype plan.
- **Switching off the official tool's own capabilities to act**, so that the mind returns text only (first prototype plan, section 2).
- **A rehearsal on an ordinary computer** before any robot (first prototype plan, the first test).
- **A bridge from ROS 2 to anonymous channels**, kept as a possible lead (see D-06).

### Open

- **Inventory through Linux.** The framing note allows Ipse to inventory what Linux reports, as hypotheses to be confirmed by experiment; whether the model should instead be prevented from reading the hardware configuration has not been explicitly settled.
- **Curiosity rising with boredom**, as long as nothing is learned.
- **Fetching perception models from the network** according to need, as proposed by Ruben; how far this goes is not settled.
- **"Doing good" and "respecting the law".** Values mentioned by Ruben, not yet classified.
- **The open questions of the framing note**, including whom Ipse trusts, the thresholds of each instinct, and the choice of the second body.
