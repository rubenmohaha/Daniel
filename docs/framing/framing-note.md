# The discovered body: framing note

Ruben · version 2.9, 26 November 2026

> Status: research document, with no implementation. Version 2.0 replaces the three-layer architecture of earlier versions with a simpler model built on a biological analogy. Novelty claims are stated as hypotheses to be confirmed, not as results. Related work is detailed in the [literature review](../literature-review/literature-review.md).

## Objective

Ipse must be able to discover itself and to improve itself.

The project aims to propose a standard and an algorithm, in the manner of an operating system, that give this ability to any robot. The body is not described to the system: the system discovers it.

## The model in brief

Ipse is defined by what it cannot change, what it can change, and how humans relate to it.

| Element | Biological equivalent | Can Ipse modify it? |
| --- | --- | --- |
| Linux | Nerves and blood vessels | No |
| Built-in language model | An adult mind | No |
| Instincts | Innate drives | No |
| Everything the model writes: body description, code, skills, memory | What is learned during a lifetime | Yes: this is where improvement happens |

Humans do not intervene inside Ipse. They communicate with it through its senses: voice, hearing, sign language and other perceivable signals.

### An adult mind in an unknown body

Ipse is not a newborn. The language model already knows a great deal: what a wheel or a camera is, what walking means, how to speak. What it does not know is which of its channels does what. Ipse is therefore best understood as an adult mind waking up in a body it has never seen.

Two consequences are accepted as part of the design:

- **The mind does not grow.** The model is fixed, so Ipse does not become more intelligent with experience. What grows is its knowledge of its body and its know-how, in written form. Its ceiling is that of the model; when a better model becomes available, the mind can be replaced and everything Ipse has written is kept.
- **Prior knowledge provides hypotheses, reality decides.** Discovery is reasoned rather than random: a few trials suggest "this resembles two driven wheels", and the suggestion is then verified. Verification is required precisely because a confident adult can be wrong about an unfamiliar body.

## How it works

The architecture is simple. The language model runs as an agent inside a harness, and manages itself.

- **The model sets its own pace.** No external clock dictates its turns. It decides when to think, when to act, and when to wait, as an agent does in a harness.
- **The model consults records when it chooses.** What the senses perceive, the levels of the instincts and the commands sent can be looked up at will; nothing is pushed to the model at each turn.
- **The model has a memory of its own.** Its purpose is to understand the environment, to retain what is essential and relevant, and to let the model concentrate on what matters, such as its code and its trials.
- **The model improves by experiment.** It analyses, rewrites what it has written, and tests the result in the real world.

Records and memory age differently. Raw records only accumulate, and the oldest are lost over time whatever their content. The memory forgets by relevance: the model decides what stays. Anything worth keeping must therefore be carried into memory before it fades.

### Where the records come from: an open point

Whether Ipse needs a dedicated log of its own is not settled. Two options are under consideration:

- **Linux provides them.** The system already keeps records of what happens; Ipse adds no log of its own and the model reads what the system offers.
- **The model builds them.** The model sets up the recording it needs, when it needs it, as part of what it writes.

The choice bears on the principle "observed, not declared" stated below. If the model builds and maintains its own records, the measurements used to judge an improvement are produced by the party being judged. Records that the model can read but not rewrite would preserve the principle; this remains to be decided.

## What is fixed

### Linux

Ipse runs on top of Linux as a continuously running program. It is not an operating-system kernel; the term "operating system" describes its role with respect to the robot, not its technical nature. Linux carries signals between the body and the rest of the system, as nerves and vessels do, and Ipse cannot modify it.

### The built-in language model

Ipse ships with a large language model by default. This model is not modified and not retrained. It is the component that reasons: it formulates hypotheses, discovers the body, and writes code. This matches the approach of every self-improving robotic system reviewed, all of which keep the model frozen and improve what surrounds it.

The model is multimodal and has open weights, so that any robot can embed it. The working reference is Qwen3.8, released under the Apache 2.0 license; whether its smaller variant handles images and sound, and what hardware it requires, remain to be verified. The standard specifies the kind of model, not a particular one.

### The reflection loop

The model writes to itself. At each turn it has its previous thought and whatever it chooses to consult: the current levels of its instincts and what its senses have captured, even when unclear. It then writes its next thought or decides to act. The rhythm of these turns is the model's own.

A model retains only a limited amount of text. What matters must therefore be written to memory, which sleep later sorts.

### The instincts

Instincts are modelled on those of animals and restricted to the essentials. Five keep Ipse alive; one makes it grow.

| Instinct | For Ipse | Without it |
| --- | --- | --- |
| Hunger | Recharge the battery | It shuts down |
| Temperature | Slow down or stop when overheating | It damages its components |
| Sleep | Rest, in order to clean up its code and memory, when working memory or storage fills up | It saturates its memory and storage until it no longer works |
| Pain | Withdraw at once on impact or when a motor strains | It breaks |
| Fear | Freeze, or proceed gently, when facing the unknown | It endangers itself before it has understood |
| Curiosity | Go towards what it does not yet understand | It stays on its charger and never discovers anything |

The limits of the computer that hosts Ipse belong to these vital instincts, in the same way as the battery. Working memory and disk space are finite resources of the body: their saturation is a fatigue signal that triggers sleep, and it restrains curiosity, since acquiring new code, data or models consumes storage.

The first five are sufficient for survival but admit a trivial strategy: remaining plugged in and motionless. Curiosity is what drives body discovery and self-improvement, and is therefore kept as a sixth instinct of a different kind.

Other animal behaviours are deliberately not instincts: play, imitation, attachment, returning to the charging base, signalling, self-inspection. Ipse can discover or learn them, precisely because the six instincts push it to. Returning to its base, for instance, need not be innate: hunger is enough for it to be learned.

### Everything else follows from the instincts

No developmental stage is programmed. Behaviours follow from the same few instincts:

- **Safety comes before curiosity.** Ipse explores only when its five vital instincts are quiet. Safety is not a seventh instinct: it is the state in which the vital instincts are satisfied.
- **Exploratory movement, practice and communication are curiosity.** They are successive objects of the same drive. Ipse's curiosity is directed at itself rather than at the world, about which the model already knows a great deal.
- **The link between movement and sensation is learned from repetition**, as described below.

Obeying a spoken command such as "stop" is not an instinct either. The model already understands language, but Ipse must first discover which of its streams is a microphone.

## What evolves

Everything the language model writes can be rewritten by it:

- the **body description**: what each channel does, established by experiment;
- the **code**: drivers and the control interface derived from the description;
- the **skills**: gestures that succeeded and were kept;
- the **memory**: what the model has understood of its body and its environment, and has chosen to retain as essential and relevant.

Self-improvement means changing these, never the three fixed elements.

## The human

The human relates to Ipse as a parent or a teacher does, not as a programmer. Nothing is edited from the inside; everything passes through the senses.

One consequence follows directly: at the very beginning, Ipse does not know that one of its input streams is a microphone. It already knows how to communicate, but must discover its senses before it can listen or answer. Communication with humans is thus an outcome of discovery, not a starting point.

## Discovering the body

### The starting point

No human writes a description of the robot for Ipse. This is the project's commitment: no manual, no adapter, no model of the body prepared in advance.

Being an adult mind, Ipse knows how to use Linux, and may use it to find out what is connected: a camera, a microphone, a board driving four motors, a battery. This inventory is obtained in seconds, and it is legitimate, in the way a person looks at their hands before moving them.

What the system reports and what it does not must be distinguished:

- **What Linux reports** is an inventory of components.
- **What Linux does not report** is which motor turns which wheel, in which direction, with what force, or whether two cables have been swapped. This can only be learned by trying.

The rule follows: the inventory provides hypotheses, experiment confirms them. Nothing enters the body description without having been observed.

Some bodies offer no inventory at all. On a board with raw inputs and outputs, such as a Raspberry Pi driving general-purpose pins, Linux says nothing about what is wired to them. Ipse must then test its outputs and look for the stimuli that come back. The method below covers both cases: with an inventory, it verifies; without one, it discovers.

Discovering a body from uninterpreted sensors and effectors has a precedent in Pierce and Kuipers (1997), who derive control laws from such a starting point. The intended contribution here is what is derived: a readable description, a generated control interface, and their repair.

### The minimal loop

The minimal element is a loop: act, perceive, compare with what was expected. The prediction error is the signal that curiosity follows: explore where prediction still fails but learning remains possible.

### Open bets

Ipse can issue several actions at once and wait for one response or a sequence of responses. The basic unit is a bet: actions issued, an expected response, a timeout. Each bet ends confirmed, contradicted or expired. No response within the timeout is itself information: the link does not exist, or the body has changed.

To attribute a response to a channel:

- **In isolation first, in combination later.** Each channel's effect is learned alone before combinations.
- **Sign every action.** Each channel is excited with its own random sequence, and Ipse looks for which sequence appears in which input.
- **Intervene.** Send the command at randomly drawn times, then withhold it, and compare.

### The link table

A link is learned from repetition, in four steps:

1. **A record.** For each movement, Ipse keeps what was commanded, what the senses perceived just before, and what they perceive just after.
2. **Repetitions.** A single occurrence proves nothing. The same movement is repeated many times, at randomly drawn moments, and sometimes deliberately withheld for comparison.
3. **A count.** For each pair of one command and one sense: when the command was sent, did the sense change? When it was not sent, did the sense change anyway?
4. **A table.** Each row is a link that strengthens or fades.

| Command | Sense that responds | Delay | Confirmed | Refuted | Verdict |
| --- | --- | --- | --- | --- | --- |
| Channel 3 | Stream 7 | 0.2 s | 18 | 2 | Solid link |
| Channel 3 | Stream 2 | 1 s | 9 | 11 | Coincidence |
| Channel 5 | Stream 1 | 0.1 s | 20 | 0 | Certain link |

The record and the count are mechanical and fast; they do not involve the language model. The model reads the table from time to time, formulates hypotheses, chooses the next experiment, and writes the body description from the solid links.

Curiosity directs Ipse to the rows that are still uncertain. When a link that was certain suddenly starts to fail, the body has changed: this is the situation the rewiring test creates.

## One logic at every level

An action may be simple or complex, but the logic is the same at every level: try, observe, count, keep the better. Only the level of control differs. Moving an arm can be measured; so can going from point A to point B, which involves many steps that cannot all be known in advance.

### Functions

Every function, whatever its level, is described in the same way:

- what it seeks to obtain;
- how it proceeds, that is, which simpler functions it calls;
- its observed measures: time, precision, number of trials;
- its previous versions.

Functions stack, each calling the level below:

```
go from A to B
 ├─ walk
 │   ├─ place a foot
 │   │   └─ commands on channels
 │   └─ keep balance
 └─ climb stairs   (not yet learned)
```

The link table is the lowest level: a command is sent, and something happens. Above it, the structure is the same, with functions in place of commands. As functions accumulate, calls are made at an ever higher level.

### Consequences

- **What is mastered becomes automatic.** A reliable function runs without the language model, as a person walks without thinking about walking. The model attends only to the highest level and to what fails.
- **Nothing needs to be planned in advance.** To reach a goal, Ipse composes what it already knows how to do. Where a function is missing, it fails, and that is where curiosity sends it.
- **Every improvement is recorded at its own level, and confirmed above.** A faster step may make walking faster, or unbalance it. When a function changes, the functions that call it are measured again, and the previous version is kept if the level above degrades.

### Senses

The instincts determine which signals a body must provide. Each instinct needs a signal to act on:

| Instinct | Signal required | Typical sensor |
| --- | --- | --- |
| Hunger | Energy level | Battery gauge |
| Temperature | Internal temperature | Thermal sensor |
| Sleep | Fatigue: working-memory load and storage usage | System memory and disk gauges |
| Pain | Danger signal | Impact detection, motor current spikes |
| Fear, curiosity | Prediction error | Any stream; an inertial unit and proprioception respond fastest |

A body must therefore provide roles (an energy signal, a temperature signal, a danger signal) rather than specific sensors, consistent with defining interoception by function rather than by physical origin (Candia-Rivera, arXiv:2604.24527). Vision and hearing are not required for survival; they are what makes communication with humans possible.

### Perception

Raw streams serve two purposes, at two levels:

- **Numbers for the link table.** Whether a stream changed when a command was sent is computed directly on the signal, or on a compact numerical summary of it, quickly and without the language model.
- **Words and images for reflection.** A multimodal model perceives images directly, which avoids a separate captioning model. Transcription alone would not suffice for hearing: it keeps speech and discards the other sounds, such as motor noise or an impact, that matter for discovering the body.

Ipse may also fetch specialised models from the network when it needs them. This is consistent with body discovery only in one order: Ipse first establishes by itself that a stream behaves like an image or a sound, then fetches a suitable tool. A fetched model is a function like any other: it belongs to what evolves, is measured, and is kept only if it improves performance. It never touches the three fixed elements.

The literature supports proprioception as the basis of a self-model, and partially supports internal-state signals as a source of motivation. No work reviewed measures the effect of removing an internal signal on body learning: such an ablation is a possible contribution of the project.

## Sleep

The day adds, the night removes. During activity, Ipse acts, makes mistakes and learns, and what it has written grows. During sleep, it stops and cleans up: code that is never called or never succeeds is removed, duplicates are merged, the rest is simplified.

- **Rare does not mean useless.** A manoeuvre used once a month must be kept. What fails, or what is superseded, is removed.
- **Archive rather than delete.** Anything removed by mistake must be restorable.
- **Storage is finite.** The archive itself is bounded by the disk: when storage approaches its limit, the oldest archives are the first to go.
- **Waking check.** A cleaned-up version is adopted only if its behaviour is unchanged. Same behaviour, less code: this is a non-regression check, easier to verify than an improvement.

The literature reviewed supports the waking check: *Let Them Sleep* (arXiv:2610.25561) prunes an agent's memory without a non-regression test and ends 19.5 points below the baseline in an adverse case. No work reviewed adopts a cleaned-up version on the condition of identical behaviour.

## What "better" means

A version is better if it performs the same task faster or more precisely.

These two measures are deliberately simple. Four conditions give them meaning:

- **One measure must not be traded for the other.** A version is better if it improves speed or precision without degrading the other. A version that is faster but less precise is different, not better.
- **The task must be completed.** A faster attempt that fails is not an improvement.
- **The instincts still apply.** They are fixed and cannot be traded for speed: a version that goes faster by ignoring pain or fear is not available to Ipse.
- **The comparison is repeated.** Time and precision vary from one trial to the next, so a version is compared over several repetitions rather than a single run.

Time and results are observed, not declared. Ipse cannot modify reality: the time a task takes and the outcome it produces are facts of the physical world. Time is read from the clock of the fixed part of the system, which Ipse cannot change, and the result is whatever can be observed in the world once the task is done. What Ipse writes about its own performance is not a measurement.

The same criterion applies to body discovery itself: the time needed to rediscover the body after a change, and the accuracy of the resulting description, are measured like any other task.

## Demonstration and success criterion

The first proof to deliver is generality with respect to the body: the same code discovers two very different bodies without a single body-specific line.

| Body | Nature | Outputs | Inputs |
| --- | --- | --- | --- |
| No. 1 | Four-wheeled base, physical | Motors, speaker | Camera, microphone, inertial unit |
| No. 2 | Very different simulated body, for example a two-joint arm | To be defined | To be defined |

Protocol:

1. Ipse receives no description of the robot. It may inventory what Linux reports.
2. It sends small signed pulses on each channel and observes the changes.
3. It formulates hypotheses and tests them.
4. It writes its body description and a calibrated control interface.
5. Two motor cables are swapped: it must detect this and repair itself without intervention.

Success criterion, for each of the two bodies and without any code change: a correct body description, a working control interface, and a successful repair after rewiring.

Initial trials are run with the wheels off the ground or in an enclosure, since random pulses can move the robot unpredictably.

## Related work and positioning

Details are in the [literature review](../literature-review/literature-review.md), which was written against version 1.0 of this note.

| Work | Content | Difference from this project |
| --- | --- | --- |
| [Pierce and Kuipers](https://web.eecs.umich.edu/~kuipers/research/pubs/Pierce-aij-97.html), 1997 | Discovery of a sensorimotor apparatus from uninterpreted sensors and effectors | No readable description, no generated code, no reasoning model |
| [KnowBody](https://arxiv.org/html/2609.28530v1), September 2026 | Structured, versioned body model with per-value provenance; one physical arm | Kinematic chain declared at the start, no generated control code, no rewiring |
| [EAISys](https://github.com/Interactive-Active-AI/EAISys), 2026 | Without a URDF, an agent probes a simulated arm joint by joint, then controls it | Single run in simulation, no written description, no rewiring test (README read only) |
| [HexaShell](https://github.com/HexaFuture/HexaShell), October 2026 | A vision-language model writes Python; a second agent writes or fixes tools after a failure | Each robot requires an adapter and a written description |
| [iAm.md](https://arxiv.org/html/2610.10962v1), October 2026 | Textual robot identity file generated by an agent from the URDF and the ROS 2 graph | Nothing is established by experimenting on the body |
| [PhyAgentOS](https://arxiv.org/abs/2607.16636), July 2026 | Self-improving robotic OS: memory and skills evolve, safety constraints are immutable | Robots are added through hand-written adapters; the body is described |
| [Bongard et al.](https://static.ias.edu/pitp/archive/2012files/Resilient_Machines%28Science06%29.pdf), 2006; [Hu and Lipson](https://arxiv.org/abs/2311.12151v2), 2025 | Self-model built through action; adaptation after damage | Morphological damage rather than channel permutation; no reasoning model |

Each element exists somewhere in isolation. According to the review, no work read chains them together: no human-written description of the robot, experimentation, a description written by the robot, a generated control interface, and repair after rewiring. Proposed formulation, to be confirmed:

> An algorithm that, without any human-written description of the robot and driven by a small set of fixed instincts, inventories what the system reports, discovers the body by experiment, writes its description and its control, and then improves, validated on two very different bodies without body-specific code.

The contributions least covered by the literature reviewed are the rewiring test, the waking check, and the use of a minimal set of animal-like instincts as the only fixed drives of a self-improving robot. The last point has not yet been checked against the literature on homeostatic and intrinsically motivated agents. An absence in search results is not proof of absence, and timing is a risk: several 2026 systems are each advancing on part of the problem.

## Open questions

- **Whom Ipse trusts.** If humans communicate only through the senses, anyone can address it. Should it trust everyone, or learn to recognise particular people?
- **Limits of safe testing.** Earlier versions gave each output channel bounds fixed in advance. Without a human-written description, what keeps the first trials on an unknown output within safe limits, before pain can be felt?
- **Acting without external stimuli.** Should curiosity rise as long as nothing is learned, and fall only when learning is observed rather than declared?
- **Fast responses.** Mastered functions run without the model, but pain and fear must also act faster than it can respond: where do the instincts themselves run?
- **Tuning the instincts.** At what thresholds does each instinct act?
- **Dependence on the network and on hardware.** Fetching models requires a connection, and a multimodal model requires substantial computing power on the robot.
- **Second body.** Simulated arm, simulated drone, or something else?
- **Generality with respect to the task.** Second proof, after generality with respect to the body.

## Next steps

- [x] Create the repository and add this note
- [x] First literature review on body discovery by an agent
- [ ] Extend the review to homeostatic and intrinsically motivated agents, and to developmental robotics
- [ ] Verify the capabilities and hardware requirements of the reference model
- [ ] Specify the signals each instinct requires from a body
- [ ] Specify each instinct as a verifiable condition
- [ ] Choose the second body
