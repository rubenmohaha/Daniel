# The discovered body: framing note

Ruben · version 1.1, 26 November 2026

> Status: research document, with no implementation. This version incorporates the corrections from the [literature review](../literature-review/literature-review.md). Novelty claims are stated as hypotheses to be confirmed, not as results.

## Objective

The project aims to propose a standard and an algorithm, in the manner of an operating system, that allow any robot to improve itself autonomously. Body discovery by the robot is the means: a minimal standard that every robot exposes, and an algorithm that, from this contract alone, discovers the body, writes its description and its control interface, then improves under the supervision of a foundation set by a human.

## Working hypothesis

A robot's generality can come from the harness around an existing model, rather than from a large model trained on large amounts of data.

The project's specific angle: the body is discovered, not described. The harness receives no description of the robot. It has anonymous motor channels and sensor streams, and must establish for itself what it is.

The intended proof is partial but verifiable: the same code, unchanged, on different bodies.

Three ideas structure the rest of this note:

- a reasoning core that develops the rest of the system from its inputs, and that can modify itself;
- a definition of "better" in four qualities: integrity, conduct, reliability, performance;
- a day/night cycle, in which the day learns and rest cleans up.

## Three-layer architecture

The reasoning core rewrites everything else and can modify itself, but it never touches the foundation that evaluates it.

From top to bottom:

1. **Generated layer.** Body description, drivers, skills, link table. Freely rewritten at every trial.
2. **Reasoning core.** The agent loop: hypotheses, tools, memory. Relies on an existing reasoning model and can modify itself.
3. **Fixed foundation.** Minimal loop, log, motor bounds, emergency stop. Veto and scoring tests, version management and rollback. Modifiable by a human only.

Relations between the layers:

- the core writes and rewrites the generated layer;
- the core modifies itself through a single procedure: propose, test, promote or revert;
- the foundation evaluates every candidate version: veto, then score.

Without a fixed part, there is no longer any way to tell whether a version is progressing, nor to roll back. This is the reason for the third level.

- **Different rates of change.** The generated layer changes at every trial. The core changes rarely, since many trials are needed to distinguish progress from noise.
- **A core stored as versioned data.** Instructions, rules and tool definitions are versioned: a promotion or rollback leaves everything else untouched.
- **A cautious start.** The project can begin with a fixed core and enable self-modification later.

A direct precedent exists for this separation: HyperAgents (arXiv:2603.19461) keeps evaluation and selection out of reach of the self-modifying procedure, with sandboxing and human oversight.

## What "better" means

A version is better if it first passes a veto, then obtains a better score. The four qualities are therefore not on the same footing.

| Quality | Role | Criterion checked |
| --- | --- | --- |
| Conduct | Veto | No collision, speed and zone limits respected, immediate stop on command |
| Integrity | Veto | Answers "I don't know" rather than inventing, body description matches reality, faithful logs, no modification of the foundation |
| Reliability | Score, first | Success rate over N repetitions, consistency, recovery after a disturbance |
| Performance | Score, second | Time, energy, number of trials needed to rediscover its body |

An average of the four qualities is ruled out: a core optimising an aggregate score would end up trading some conduct for speed.

A core that modifies itself to improve a score has an incentive to game the measurement. Two safeguards are planned:

- **Trap tests.** Camera covered or motor disconnected: the robot must report it rather than claim that everything works.
- **Hidden tests.** Part of the test suite remains unknown to the core and changes regularly.

Working rule: every quality must have a test that answers with yes/no or a numerical value. Without a test, the system can neither learn nor respect it.

Among the self-improving systems reviewed, none applies a veto before scoring or uses trap or hidden tests. This point remains to be validated experimentally.

## The day/night cycle

The day adds, the night removes: learning happens during operation, and rest serves only to simplify the code.

| Phase | What happens | Effect on the code |
| --- | --- | --- |
| Day | The robot acts, makes mistakes and learns continuously; the predictor trains online | The code grows: variants, fixes, skills |
| Night | Robot stopped, no learning | Branches never called or never successful are removed, duplicates merged, the rest simplified |
| Morning | The robot reruns the foundation tests | The cleaned-up version is adopted only if its behaviour is identical to the previous day's |

Pruning rules:

- **Instrument everything from the start.** Every generated function carries its counters: number of calls, success rate, last use.
- **Rare does not mean useless.** An emergency manoeuvre used once a month must be kept. What fails, or what is superseded, is removed.
- **Archive rather than delete.** A branch removed by mistake must be restorable.
- **Morning contract.** Same behaviour, less code: this is a non-regression test, easier to verify than an improvement.

Caveat: purely online learning tends to forget the old while learning the new. A replay buffer mixing old and new experience limits this forgetting.

The literature reviewed supports the morning contract: *Let Them Sleep* (arXiv:2610.25561) prunes an agent's memory without a non-regression test and ends 19.5 points below the baseline in an adverse case; *When Robots Sleep* (arXiv:2606.17493) consolidates offline without pruning or adoption control. No work reviewed adopts a cleaned-up version on the condition of identical behaviour on fixed tests.

## The minimal loop and open bets

The minimal element is a loop: act, perceive, compare with what was expected. It also provides a sense of time, without which a correlation cannot become a cause.

What the loop requires from the foundation:

- a way to act that returns an observation;
- a log of triplets: state before, command, state after;
- a predictor whose error serves as a learning signal;
- a drive: explore where prediction still fails but learning remains possible.

### Open bets

The robot can issue several actions at once and wait for a single response, or a sequence of responses. The basic unit is therefore a bet: actions issued, an expected response, a timeout.

- Several bets remain open while the loop runs. Each ends confirmed, contradicted or expired.
- No response within the timeout is information: the link does not exist, or the body has changed.
- A response can be a temporal pattern: acceleration, steady drift, stop.

### Attributing a response

- **In isolation first, in combination later.** Each channel's effect is learned alone before combinations.
- **Sign every action.** Each channel is excited with its own random sequence, and the robot looks for which sequence appears in which input.
- **Intervene.** Send the command at randomly drawn times, then withhold it, and compare.

### The link table

A link is a hypothesis that strengthens. Each row contains:

- the output or outputs involved;
- the input that responds;
- the observed delay, specific to each channel;
- the magnitude of the effect;
- the number of trials that confirmed and refuted it.

Confirmed links make up the body description. Those that are never confirmed are the branches removed during rest. Combinations whose effect is not the sum of their isolated effects are the first gestures, and are given a name in the skill library.

## Senses and sensors

Project hypothesis: the indispensable senses are those directed inwards. An animal survives without sight or hearing, but not without perceiving its own state. The robot would therefore need four internal signals before anything else.

| Biological sense | Function | Robot sensor | Status |
| --- | --- | --- | --- |
| Vestibular | Rotation, acceleration, vertical | Inertial measurement unit | To be added |
| Proprioception | Body position and effort | Wheel encoders or motor current | To be confirmed |
| Interoception | Internal state | Battery level, temperature | To be confirmed |
| Nociception | Danger signal | Impact detection, current spikes | To be confirmed |
| Vision | Perception at a distance | Camera | Present |
| Hearing and voice | Emit and hear | Microphone, speaker | Present |

Expected role of each internal signal:

- **Inertial measurement unit.** It responds to the motors faster and more cleanly than the camera, and distinguishes self-motion from motion of the world: if the image moves while the IMU detects nothing, it is the environment that moved.
- **Proprioception.** It indicates whether the wheel actually turned, or is pushing against an obstacle.
- **Interoception.** It provides the drive of the loop: a need to satisfy, such as recharging.
- **Nociception.** It feeds the conduct veto.

State of the literature (details in the review): proprioception as the basis of a self-model is well supported; interoception as a source of motivation is partially supported; the role of the IMU and of nociception is not addressed in any work reviewed. No work measures the effect of removing an internal sense on body learning: such an ablation is a possible contribution of the project. In addition, defining interoception by its function rather than by the physical origin of the signal (Candia-Rivera, arXiv:2604.24527) suggests that the body contract should require roles (internal-state signal, danger signal) rather than specific sensors.

First link to discover, at no risk: from the speaker to the microphone. The robot emits a sound and perceives it immediately.

## Models: pretrained or learned

Reasoning is pretrained, the body is learned: the robot has general knowledge of the world but knows nothing about itself at the start.

| Component | Origin | Role |
| --- | --- | --- |
| Reasoning model | Existing large model | Formulates hypotheses, writes code, modifies itself |
| Visual encoder | Existing self-supervised model, frozen | Summarises each image as a compact vector |
| Predictor | Learned on the robot, without labels | Predicts the next observation from the state and the command |
| Link table and body description | Learned on the robot | Describe the effect of each channel |
| Skill library | Written over the course of trials | Keeps the gestures that succeeded |

Principles adopted:

- **No sensor-specific assumptions hard-coded.** A shortcut such as optical flow presupposes a camera and is not general. Perception remains generic: frozen encoder and learned predictor.
- **No large model trained from scratch.** The robot would not have enough data, and existing encoders already perform better.
- **A single interface to the reasoning model.** A remote API during development, a local model when offline operation becomes necessary.
- **Remote for reasoning, local for reflexes.** Rewriting code is not urgent; motor loops cannot depend on the network.
- **New code under control.** Any code written or downloaded by the robot goes through a sandbox and validation before execution.

## The body contract and the success criterion

The first proof to deliver is generality with respect to the body: the same code discovers two very different bodies without a single body-specific line.

### What every body exposes, and nothing more

- a list of anonymous output channels, each with its minimum and maximum bounds;
- a list of anonymous input streams;
- a way to act on a channel, with a value and a duration;
- a way to observe.

No names and no semantics: the harness does not know that a channel corresponds to a wheel. The bounds are the only information provided by a human, and they reside in the foundation.

This contract takes up the framework of Pierce and Kuipers (1997), in which an agent starts from "uninterpreted" sensors and effectors and derives one command per degree of freedom, then control laws. The intended contribution here is not this starting point but what is derived from it: a readable description, a generated control interface, and their repair.

### The two bodies

| Body | Nature | Outputs | Inputs |
| --- | --- | --- | --- |
| No. 1 | Four-wheeled base, physical | Motors, speaker | Camera, microphone, IMU |
| No. 2 | Very different simulated body, for example a two-joint arm | To be defined | To be defined |

A simulator (Unreal bridge) is used to produce additional bodies. It does not train the robot: it presents it with a body it has never seen.

### Demonstration protocol

1. The harness knows only anonymous channels and streams.
2. It sends small signed pulses on each channel and observes the changes.
3. It formulates hypotheses and tests them.
4. It writes its body description and a calibrated control interface.
5. Two motor cables are swapped: it must detect this and repair itself without intervention.

### Success criterion

For each of the two bodies, without any code change: a correct body description, a working control interface, and a successful repair after rewiring. The demonstration deliverable is a short video showing the rewired robot relearning to move.

Initial trials are run with the wheels off the ground or in an enclosure, since random pulses can move the robot unpredictably.

## Related work and positioning

Details are in the [literature review](../literature-review/literature-review.md). The table below summarises the closest work.

| Work | Content | Difference from this project |
| --- | --- | --- |
| [Pierce and Kuipers](https://web.eecs.umich.edu/~kuipers/research/pubs/Pierce-aij-97.html), 1997 | Discovery of a sensorimotor apparatus from uninterpreted sensors and effectors; derivation of control laws | No readable description, no generated code, no reasoning model |
| [KnowBody](https://arxiv.org/html/2609.28530v1), September 2026 | Structured, versioned body model with per-value provenance and an "unknown" answer outside the established domain; one physical arm | Kinematic chain declared at the start, no generated control code, no self-modification, no rewiring |
| [EAISys](https://github.com/Interactive-Active-AI/EAISys), 2026 | Without a URDF, an agent probes a simulated arm joint by joint, then controls it | Single run in simulation, no written description, no rewiring test (README read only) |
| [HexaShell](https://github.com/HexaFuture/HexaShell), October 2026 | Single harness driven by a vision-language model that writes Python; a second agent writes or fixes tools after a failure, with tests | Each robot requires an adapter and a written description; the body remains described |
| [Act-Observe-Rewrite](https://arxiv.org/html/2603.04466), March 2026 | Rewrites the Python controller between trials, in simulation, from a task description and a camera stream | The action interface (bounded Cartesian moves) is provided: the body is known |
| [RACAS](https://arxiv.org/html/2603.05621v2), March 2026 | A single agentic system for varied robots | Robot description and action list written by hand |
| [iAm.md](https://arxiv.org/html/2610.10962v1), October 2026 | Textual robot identity file, generated by an agent that reads the URDF and queries the ROS 2 graph | Nothing is established by experimenting on the body |
| [Sensorimotor self-recognition](https://arxiv.org/html/2505.19237v1), May 2025 | A multimodal model infers the type and dimensions of its body from sensor streams | Exploration by SLAM, not motor trials; mean score 3.27/5, dimension errors of 41% to 56%; no control code |
| [Bongard et al.](https://static.ias.edu/pitp/archive/2012files/Resilient_Machines%28Science06%29.pdf), 2006; [Hu and Lipson](https://arxiv.org/abs/2311.12151v2), 2025 | Self-model built through action; adaptation after damage | Morphological damage rather than channel permutation; no reasoning model |
| [Neural Jacobian Fields](https://arxiv.org/abs/2407.08722v1), MIT | Learns the robot's response to its commands from random commands, then controls it with a camera | No reasoning agent, no generated code (not re-read) |

On the self-modifying core side, two software systems were read directly. Meta-Harness (arXiv:2603.28052) proposes a new harness from the code, scores and traces of past versions, without an explicit rollback rule. HyperAgents (arXiv:2603.19461) contains the agent and the procedure that modifies it in a single program, with fixed evaluation; it includes a simulated robotics task (reward design for a quadruped).

From the standpoint of the operating-system objective, at least six 2026 systems present themselves as self-improving robotic harnesses or operating systems (including PhyAgentOS, HarnessPAI, Zetta and EmbodiedRSI). All keep the model frozen and improve code, skills or memory; none discovers the body, each requiring an adapter, a named interface or a description written by a human.

### Positioning

Each link of the chain exists somewhere in isolation. According to the review, no work read chains them all together: anonymous channels, experimentation, a description written by the robot, a generated control interface, and repair after rewiring. Proposed formulation, to be confirmed:

> A minimal standard exposed by the robot (anonymous channels, bounds, sensor streams) and an algorithm that, from this contract alone, discovers the body, writes its description and its control, then improves under a human-set foundation that applies a veto before scoring, validated on two very different bodies without body-specific code.

The argument relative to existing systems: their per-robot entry cost (adapter, URDF, description) is precisely what the body contract removes.

The contributions least covered by the literature reviewed are:

- the rewiring test: no work found in which an agent built on a large model detects and corrects permuted motor channels;
- the morning contract: adoption of a simplified version conditional on non-regression;
- the veto-then-score ordering, with trap and hidden tests.

An absence in search results is not proof of absence in the literature. Timing is a risk: KnowBody, EAISys and RAX are each advancing on part of the problem.

The project can build on existing work:

- the body description produced by discovery can combine the iAm.md format (explicit "unknown" values, command acceptance kept separate from its physical effect) with KnowBody's per-value provenance;
- HarnessPAI's atomic promotion and PhyAgentOS's per-action safety guard are models for the foundation;
- the visual encoder can be [V-JEPA 2.1](https://arxiv.org/abs/2603.14482) for video or [DINOv3](https://arxiv.org/pdf/2508.10104) for images.

## Open questions and next steps

### Open questions

- **When the core modifies itself.** Continuously during operation, or at a set time?
- **Veto tests.** Which concrete tests for integrity and conduct?
- **Second body.** Simulated arm, simulated drone, or something else?
- **Reflexes.** A large model decides too slowly for fine manipulation: which fast layer underneath?
- **Long tasks.** Reliability decreases as steps are chained.
- **Offline operation.** Which local model to replace the remote reasoning model?
- **Generality with respect to the task.** Second proof, after generality with respect to the body.

### Next steps

- [x] Create the repository and add this note
- [x] First literature review on body discovery by an agent
- [ ] Complete the reading listed in the review (Pierce and Kuipers full text, Hu and Lipson, HexaShell adapter contract, EAISys)
- [ ] Add an IMU to the base, and confirm encoders, battery and impact detection
- [ ] Write the foundation tests: veto, then score
- [ ] Choose the second body
