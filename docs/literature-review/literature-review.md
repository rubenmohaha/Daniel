# Literature review: the discovered body

Version of 26 November 2026

> Update of 26 November 2026: a section on equivalents to the version 2 model has been added (see "Update: equivalents to the version 2 model").
>
> Status: exploratory review, carried out during the project's research phase. It covers version 1.0 of the [framing note](../framing/framing-note.md); the corrections it recommends were incorporated in version 1.1. Version 2.0 of the note has since replaced the three-layer architecture (generated layer, reasoning core, fixed foundation) discussed here with a simpler model; the findings on related work remain applicable. The limitations of the method are described in the penultimate section.

## Summary

The position holds for the complete chain, but not in its current form. Of the 19 works read, none chains together anonymous channels, experiments, a description written by the robot, a generated control interface, and repair after rewiring. Each link taken alone already exists somewhere.

Three findings call for a reformulation:

- **Body discovery from anonymous channels dates back to 1997.** Pierce and Kuipers start from "uninterpreted" sensors and effectors and derive one command per degree of freedom, then control laws. The note does not cite them. Claiming that no one discovers their body would be false.
- **Two 2026 works are much closer than those cited in the note.** KnowBody (September 2026) builds a structured, versioned body model through interaction, on a physical arm. EAISys (GitHub repository, 2026) probes a simulated arm without a URDF, joint by joint, then controls it.
- **Repair after a change to the body has precedents** (Bongard and Lipson 2006, Hu and Lipson 2025), but for damage, not for swapped channels, and without a reasoning large model.

Proposed formulation: *the first harness in which an off-the-shelf reasoning model, facing anonymous channels, writes a verifiable body description itself, derives its control interface from it, and repairs it after rewiring, on two very different bodies without a single body-specific line.* The rewiring test and "the same code on two bodies" remain the points that nothing read covers.

The risk is timing: KnowBody, EAISys and RAX (October 2026) are each advancing on one piece. The gap may close within a few months.

**Extension: the objective is a self-improvement OS for any robot.** Body discovery is a means; the intended contribution is a standard or an algorithm, in the manner of an OS. From this angle, the field is much more crowded: at least six 2026 systems present themselves as self-improving robotic harnesses or operating systems (dedicated section below). All keep the model frozen and improve code, skills or memory. None discovers the body: each requires an adapter, a named interface or an entry written by a human.

Proposed formulation for the OS objective: *a minimal standard that a robot exposes (anonymous channels, bounds, sensor streams) and an algorithm that, from this contract alone, discovers the body, writes its description and its control, then improves under a human-set foundation that applies a veto before scoring.* The argument against competing systems: their per-robot entry cost (adapter, URDF, description) is exactly what the body contract removes.

## Table of works read

Reading depth: "full text" = full text or a large extract read; "abstract" = only the abstract or README read.

| Work | Reading | Receives at the start | Discovers on its own | Produces | Change of body |
| --- | --- | --- | --- | --- | --- |
| [KnowBody](https://arxiv.org/html/2609.28530v1), Sept. 2026 | full text | Declared kinematic chain and limits, a bootstrap trajectory | Visual response of the arm, action-effect rules, gripper-tool binding | Structured, versioned body model with provenance and "unknown" | Change of configuration or camera, no rewiring |
| [EAISys](https://github.com/Interactive-Active-AI/EAISys), 2026 | README | With URDF: the raw URDF. Without URDF: RGB cameras and encoders | Without URDF: hand in the image, camera-joint Jacobian via small pushes | Python controllers written by the model (with URDF only) | Not tested |
| [RAX](https://arxiv.org/html/2610.22496), Oct. 2026 | full text | Named interfaces: sensors, controllers, kinematics | Task strategies through online exploration | Python programs and a versioned skill library | Perturbed scenes, not the body |
| [HexaShell](https://github.com/HexaFuture/HexaShell), Oct. 2026 | README + abstract | Calibrated cameras, one-page manual, adapter of 350 to 1,450 lines | Nothing about the body | Python tools written and fixed after failure, with tests | None |
| [Act-Observe-Rewrite](https://arxiv.org/html/2603.04466), March 2026 | partial text | Task description, robosuite environment, camera stream | Nothing about the body | Python controller rewritten between trials | None |
| [RACAS](https://arxiv.org/html/2603.05621v2), March 2026 | full text | Textual robot description and JSON action list, written by hand | Nothing about the body | Actions chosen from the provided list | None |
| [iAm.md](https://arxiv.org/html/2610.10962v1), Oct. 2026 | full text | URDF, ROS 2 graph, configuration | Nothing: description generated by an agent from the files | Markdown file with a fixed schema | None |
| [Sensorimotor self-recognition](https://arxiv.org/html/2505.19237v1), May 2025 | full text | Sensor streams in JSON, 1 Hz | Body dimensions and type, roughly | JSON description, no code | None |
| [Pierce and Kuipers](https://web.eecs.umich.edu/~kuipers/research/pubs/Pierce-aij-97.html), 1997 | abstract | Nothing: uninterpreted sensors and effectors | One command per degree of freedom, sensory features | Control laws, discrete actions | Not mentioned |
| [Hu and Lipson](https://arxiv.org/abs/2311.12151v2), 2025 | abstract | Short raw videos of the robot | Morphology, kinematics, control | Self-simulation | Detects an anomaly and recovers from damage |
| [Robust Visual Embodiment](https://arxiv.org/html/2510.03677v1), Oct. 2025 | full text | Images of the arm and masks | Morphology and kinematics | Neural self-model | Announced in the abstract, absent from the text read |
| [LLM-IDEA](https://arxiv.org/html/2610.11253v1), Oct. 2026 | full text | A parameterised model, hidden properties | Parameters and force law, through experiments it designs | Mechanistic model, identifiability diagnosis | No |
| [ASIA](https://arxiv.org/html/2605.10480), May 2026 | full text | Identification problem in text, recorded data | Model architecture | Model and training code | No |
| [FAEA](https://arxiv.org/html/2601.20334v1), Jan. 2026 | full text | Gymnasium interface and exact state | Nothing about the body | Control script by trial and error | No |

Reading the table: the "Receives at the start" column splits the works into two families. Those that control well (RAX, HexaShell, AOR, RACAS) receive a described body. Those that start from nothing (Pierce and Kuipers, Hu and Lipson) write neither a readable description nor code. KnowBody and EAISys are the only ones in between.

## Corrections to the framing note

The differences described in the note are broadly accurate. Five points need correcting or qualifying.

- **HexaShell writes its own tools.** The README describes a second agent that, after a failure, "writes or fixes a tool, with its own tests". This is a growing generated layer, close to the note's day cycle. The README and the arXiv abstract ([2610.23479](https://arxiv.org/abs/2610.23479)) do not give the same figures, and the date is October 2026, not November. The body remains described: the note's distinction holds.
- **Act-Observe-Rewrite does not receive a template, according to the part read.** The text states: "the agent received only a task description, a robosuite environment and a camera stream". The controller template appears only in the automatic summary, which was not verified. The action interface (bounded Cartesian moves) is provided: the body is known.
- **Sensorimotor self-recognition is weaker than the note suggests.** Exploration is performed by SLAM, not by motor trials. The mean self-identification score is 3.27 out of 5, and the model starts at 0 out of 5, believing itself to be a "fixed measurement unit". Dimension errors range from 41% to 56%.
- **iAm.md is generated by an agent, not by a simple tool.** This agent reads the URDF and queries the ROS 2 graph live. The distinction holds: nothing comes from experiments on the body.
- **Meta-Harness and HyperAgents have now been read directly.** Details are in the section on the core. The key point: HyperAgents already includes a robotics task, reward design for a simulated quadruped.

Not re-read: Neural Jacobian Fields. The original table remains the only source on this work.

## Work missing from the note that reduces its novelty

Four works must be cited in any publication, because a reviewer will raise them.

1. **KnowBody, the closest on the body description.** The body model is a queryable object, with frame, units and uncertainty. It answers "unknown" outside the domain supported by evidence, and each value keeps its provenance. This is close to the note's integrity veto. Differences: declared kinematic chain, no generated code (the model emits waypoints), no self-modification. Result: 12 successes out of 16 against 4 out of 16 for the baseline harness, on a single physical arm.
2. **EAISys, the closest on "discover, then control".** Without a URDF, the agent "wiggles its fingers to locate its hand in the cameras" and "gently pushes each joint", then succeeds at a lifting task. Limitations noted: a single run, in simulation, no written description, no rewiring test. A low-visibility project (4 stars) with no associated paper. Read through the README only; the page dedicated to URDF-free probing could not be read.
3. **Pierce and Kuipers, 1997, the historical precedent.** "The sensorimotor apparatus and the environment are initially unknown." The agent defines one command per degree of freedom, then control laws and discrete actions. This is the note's body contract, thirty years earlier, without a large model. The line of work continues with Kuipers (learning sensorimotor structure) and with O'Regan and Philipona (sensorimotor contingencies), not read here.
4. **Bongard, Zykov and Lipson, 2006, then Hu and Lipson, 2025, on repair.** A robot builds a self-model through its own actions and adapts after damage. Hu and Lipson report anomaly detection and recovery after damage. The rewiring test remains distinct: swapping channels does not change the morphology, it changes the link table. Bongard 2006 is known here only through search results, not re-read.

Search with no result: no work found in which an agent built on a large model detects and corrects swapped motor channels. An absence in search results is not proof of absence, but it is the strongest point of novelty.

## Self-improving robotic operating systems and harnesses

None discovers the body, and none has each candidate version judged by a human-set foundation, veto then score. PhyAgentOS comes closest: its safety constraints are immutable and a guard checks every action. The closest to an "OS for any robot" is PhyAgentOS; the closest to the morning contract is HarnessPAI.

| System | What improves | What stays fixed | Adoption of a version | Adding a robot | Robots |
| --- | --- | --- | --- | --- | --- |
| [PhyAgentOS](https://arxiv.org/abs/2607.16636), July 2026, Sun Yat-sen | Memory and skills as files (KNOWLEDGE.md, LESSONS.md) | Safety constraints, model weights | A verifier judges the world state; memory consolidated after confirmation | TARGETS.md entry and hand-written adapters | Simulation, and 6 physical platforms marked as tested |
| [HarnessPAI](https://arxiv.org/pdf/2609.29166), 2026 | Phase-based program code, skill library | Action models, success contract written once | Isolated copy; on failure "the library remains exactly as it was" | Not described; task graph seeded by a human | Simulation only, 7 bodies including a humanoid and a vacuum cleaner |
| [Zetta](https://arxiv.org/html/2608.16590v1), Tsinghua | Critiques, recovery, tools | VLA policy, orchestrator | Fix kept if the task succeeds and 100% on past failures | Declarative environment registration | Simulation only |
| [EmbodiedRSI](https://arxiv.org/pdf/2610.10498), Columbia and Princeton | Code, skills, hypothesis graph, 3-level memory | VLA model, operator | Not described in the part read | Not described | Simulation, and one physical SO-101 arm |
| [Embodied-Harness](https://arxiv.org/abs/2611.27689), Nov. 2026, Zhejiang | Execution harness, memory | Actor and reflection models | Not described | Not described | Simulation, and one physical Piper arm |
| [SHAPER](https://arxiv.org/abs/2608.11350), Aug. 2026, Microsoft Research | Planning skill, context code | VLA model | Best candidate on a fixed validation set | Not described | Simulation only |
| [rosaOS](https://aclanthology.org/2026.acl-demo.47/), ACL 2026 | Nothing: an orchestration OS | Everything | Not applicable | MCP and ROS | Quadruped, wheeled robot, lamp |

What the project can reuse: PhyAgentOS's "state is a file" protocol and its per-action safety guard; HarnessPAI's atomic promotion, whose success contract excludes "a clean exit, a reached final state, a high dense reward or the writer's claim"; the separation between the model that writes and the one that diagnoses.

Not read: [ABot-AgentOS](https://arxiv.org/html/2607.10350) (rate limit) and [the Nature Machine Intelligence article](https://www.nature.com/articles/s42256-026-01186-z) on a ROS framework for large models (page refused).

## Internal senses: what the literature says

The idea is plausible but not demonstrated. No work read argues for these four internal senses as a minimal prerequisite, and none removes a sense to measure the effect on body learning. None of the operating systems above treats them as a prerequisite either: all rely on cameras and on named proprioception supplied by the adapter.

| Claim in the note | What the works read show |
| --- | --- |
| Proprioception: basis of the body description | Supported. [Chen et al. 2026](https://arxiv.org/html/2606.13222v1) distinguish self from other at 99.7% on a physical G1 humanoid by matching joints to the image. [Jiang et al. 2024](https://arxiv.org/abs/2402.18675) recover body topology "without prior knowledge", on 6 simulated robots and 1 physical one. EAISys and KnowBody also rely on encoders. Motor current as proprioception does not appear in any work read. |
| IMU: separating self from the world | Not addressed in the works read. The idea remains to be sourced. |
| Interoception: battery and temperature provide the drive | Partially supported. [Stovold et al. 2018](https://arxiv.org/pdf/1811.10033): on small physical robots, battery and temperature drive behaviour and the architecture lasts longer than fixed thresholds. The sensors were simulated. [Lee, Friston et al.](https://arxiv.org/pdf/2309.05999v2) make homeostasis the primary source of reward, in theory only. |
| Nociception: feeds the veto | Not addressed. [Candia-Rivera 2026](https://arxiv.org/pdf/2604.24527) proposes viability constraints that take priority in arbitration, without experiments. |

A useful nuance for the standard: Candia-Rivera defines interoception "not by the physical origin of a signal, but by its function". The body contract could therefore require roles (an internal-state signal, a danger signal) rather than specific sensors. This remains consistent with the rule "no sensor-specific assumptions hard-coded". [INTERO](https://ceur-ws.org/Vol-4169/paper6.pdf) (Bremen, 2025) offers a ready-made ontology for naming these signals.

What is missing and the project could contribute: a measured ablation, with and without the IMU or motor current, on body-discovery time and rewiring success.

## What to build on, layer by layer

**Generated layer (description, drivers, skills).**

- Description format: iAm.md contributes two useful rules. An unestablished value is written "unknown" in place, and acceptance of a command is kept separate from its physical effect. KnowBody adds per-value provenance and uncertainty. A description combining all three would directly serve the integrity veto.
- Drivers and tools: HexaShell (tools with unit tests, repaired after failure) and RAX (versioned skill library) show the format of a gesture library.
- Hypotheses and experiments: LLM-IDEA has a group of models propose experiments, then a deterministic ranking chooses. A diagnosis indicates whether a plateau calls for more search, a better experiment, or a different kind of experiment. It is a good model for the link table.

**Self-modifying core.**

- [Meta-Harness](https://arxiv.org/html/2603.28052v1) (Stanford, March 2026): a coding agent reads a file system containing the code, scores and traces of past versions, then proposes a new harness. No explicit rollback rule; the only protection against gaming is a manual and regular-expression audit. No robotics task.
- [HyperAgents](https://arxiv.org/pdf/2603.19461) (Meta et al.): a single program contains the task agent and the procedure that modifies it, which is itself modifiable. Evaluation and parent selection remain fixed, with sandboxing and human oversight. This is exactly the note's fixed foundation. A robotics task is included: reward from 0.060 to 0.372, against 0.348 for the default reward. The authors write that their results "do not yet establish unbounded improvement".
- Neither applies a veto before scoring, nor uses trap or hidden tests. This is a contribution specific to the project, provided it is tested.

**Day/night cycle.**

- [When Robots Sleep](https://arxiv.org/pdf/2606.17493) consolidates skills offline but prunes nothing and has no adoption control.
- [Let Them Sleep](https://arxiv.org/pdf/2610.25561) prunes an agent's memory without a non-regression test. On a conversation with 35% errors, it deleted 43% of the memory and ended 19.5 points below the baseline. This is the direct argument for the morning contract.
- No work read adopts a cleaned-up version only if behaviour is identical on fixed tests. The morning contract is the real novelty of the cycle, more than the cycle itself.

## Update: equivalents to the version 2 model

Search carried out on 26 November 2026 against the current model: a fixed adult language model running alone, with no human conversation, on a Linux robot whose body is not described to it; it inventories the hardware through Linux, confirms by experiment, writes its own functions and memory, is guided by six instincts, and keeps a version only if the clock and the senses show it is faster or more precise. Thirteen additional works were read, most only in part (reading depth given per row). The earlier findings above were checked against them and still hold.

### Summary of the update

No work found combines the five traits of the current model: continuous operation without human prompts, an undescribed body, code written and kept by the model, adoption measured by clock and senses, and innate drives. Each trait taken alone now exists, often in a stronger form than Ipse currently has.

One element should no longer be presented as novel: **an agent that inventories unknown hardware through the operating system and writes its own drivers**. Octopus Protocol (MIT and Harvard, May 2026) does exactly this from a shell and a model key, unattended, and re-onboards a device after it is moved. Its limit is the one Ipse targets: it identifies devices from their descriptors and from the web, not by experiment, and states that a bare serial device "does not distinguish" a robot arm from other boards.

### Works read in this update

| Work | Reading | Closest to Ipse on | What it lacks compared with Ipse |
| --- | --- | --- | --- |
| [Octopus Protocol](https://arxiv.org/pdf/2605.09055), May 2026 | full text | Linux inventory (`lsusb`), identification, generated driver server, self-repair, 11 h unattended | Identity from descriptors and web search, not from experiments; semantic identity of a bare serial device needs a human-supplied name; "generated code is validated but never verified"; no drives |
| [explorer-of-serial](https://github.com/podstawek/explorer-of-serial), Nov. 2026 | README | Local model alone with an unknown device on a serial line, identifies it by probing, writes and runs its own program, keeps a findings notebook, independent verifier | A single computer board, not a body; no motors or senses; one task given by a human |
| [Body Discovery of Embodied AI](https://arxiv.org/pdf/2503.19941), March 2025 | full text | Starts from signals whose effect "is unknown to the agent" and finds which objects belong to it, by randomised on/off trials | Statistical test, no language model, no code, simulation only, no body change |
| [SEAR](https://arxiv.org/html/2610.18792v1), Oct. 2026, Luma AI | partial text | Agent writes Python policies, proposes its own practice tasks, judged on held-out seeds; tested with a moved camera and a miscalibrated arm | Receives a task, a success check and named perception, kinematics and servo tools; body known |
| [What Stops Recursive Self-Improvement in Robotics?](https://arxiv.org/pdf/2609.31760), Sept. 2026 | full text | 123 automatic rounds of an agent editing its own skills | Body described by hand; simulation only; target task never solved: "changes kept passing their tests, yet the target task ... never succeeded" |
| [PEPA](https://arxiv.org/html/2603.00117), 2026 | partial text | Persistent embodied agent that sets its own goals, with battery thresholds, curiosity and personality | Fixed action repertoire and declared capabilities; writes no code; long runs in simulation |
| [Sophia](https://arxiv.org/pdf/2512.18202), Dec. 2025 | abstract and parts | Persistent agent with curiosity, mastery and relatedness drives | No body (browser sandbox); no code |
| [Self-Upgrading Embodied Agents](https://arxiv.org/abs/2611.31117), Nov. 2026 | abstract | Improves nightly without human intervention; "tests every change against its unchanged self ... and keeps only what holds" | Edits its own weights rather than written code; body discovery not addressed |
| [autonomous-os / lampOS](https://github.com/autonomous-ai/autonomous-os), 2026 | README | Open-source "operating system for physical AI" that gives existing agents (Hermes, Claude Code, OpenClaw) a body | Body declared by hand in ROBOT.md with a driver per subsystem; interaction through voice or chat |
| [ABot-Claw](https://arxiv.org/pdf/2604.10096), April 2026, Alibaba | partial text | Embodied extension of OpenClaw, one script written per task, three physical robots | Per-robot ROS adapters and capability registration; driven by user requests |
| [OpenClaw on a Jetson](https://huggingface.co/blog/andito/openclaw), Feb. 2026 | full text | General agent with administrator rights on an embedded Linux board, mounts a new drive and builds its own tools | No robot body |
| [agi-robot](https://github.com/msveshnikov/agi-robot), 2026 | README | Small robot run by a language model in continuous operation from boot | Pins hard-coded; model returns fixed JSON commands; writes no code |
| [Skild Brain](https://www.therobotreport.com/skild-ai-raises-1-4b-building-omni-bodied-robot-skild-brain/), 2026, commercial | press articles | Claims to control "any robot without prior knowledge of its exact body form" and to adapt to "loss of limbs ... or even an entirely new body" | Trained neural policy, improved by fleet data; nothing written or readable; claims not independently verified |

Re-checked from the earlier review: KnowBody still starts from a declared kinematic chain and a bootstrap trajectory, and its planner writes no code; PhyAgentOS (v1.0.0, August 2026) keeps immutable built-in skills and promotes a learned skill after three verified successes; no new public material was found for EAISys.

### Where Ipse stands

Three families now surround the project:

- **Agents that take over a computer and its peripherals** (Octopus Protocol, explorer-of-serial, OpenClaw): they discover hardware through the operating system and write their own code, unattended. They stop at identifying devices; none learns a moving body.
- **Self-improving robot harnesses** (SEAR, PhyAgentOS, HarnessPAI, the 123-round study): they rewrite code and skills under tests, but on a body that is described to them and on tasks given by a human.
- **Persistent agents with drives** (PEPA, Sophia): they run without prompts and choose their own goals from internal levels, but on a fixed action set and without writing code.

On the commercial side, the "omni-bodied" claim of Skild Brain is the closest promise to "any robot, body unknown", reached by a different route: a trained network rather than knowledge written by the robot.

### What remains specific to Ipse, and what does not

No longer specific:

- Inventorying hardware through Linux and generating drivers (Octopus Protocol).
- An agent left alone with an unknown device, identifying it by probing and keeping a findings notebook (explorer-of-serial).
- Continuous, prompt-free operation of a language model on a robot (PEPA, agi-robot).
- Drives such as battery, curiosity and fatigue guiding a language model (PEPA, Sophia).
- Keeping a change only if it beats the unchanged version on tests (Self-Upgrading Embodied Agents, HarnessPAI).
- Robustness to a moved camera or a miscalibrated arm (SEAR, at the level of one task).

Still specific, as far as this search can tell:

- **Learning what each channel of a moving body does, by experiment, with a language model**, then writing that knowledge down in readable form. Octopus Protocol stops precisely where this begins.
- **No task and no success check supplied by a human.** Every self-improving harness read receives at least one of the two; Ipse derives its own from the instincts.
- **Adoption judged by the system clock and the senses**, rather than by tests or a judge the system has written or been given.
- **The rewiring test**: still no work found in which a language-model agent detects and corrects swapped motor channels.
- **The combination as a whole**, packaged as a standard for any robot.

Risk noted for the project: the 123-round study reports that an agent's changes "kept passing their tests" without the real task ever succeeding, and names evaluator capture and memory corruption among the causes. This is the honest-error risk that the clock-and-senses rule is meant to address, and it argues for keeping that rule strict.

## Remaining reading and limitations of this review

Pages were read by an automated web reader. Beyond about 40,000 characters, the remainder arrived only as a model-generated summary: figures taken from such summaries are flagged as unverified or omitted. The search covered arXiv and GitHub, in English, without access to paid databases.

- [ ] Full text of Pierce and Kuipers 1997 and of Pierce's thesis: how are the channels identified?
- [ ] Full text of Hu and Lipson 2025: damage-detection mechanism.
- [ ] Bongard, Zykov and Lipson 2006 (Science), and Kwiatkowski and Lipson 2019 on self-models.
- [ ] EAISys page on URDF-free probing and its execution traces, blocked by a rate limit.
- [ ] HexaShell adapter contract, to measure what a new body actually costs.
- [ ] Sections 5.2 onwards of Act-Observe-Rewrite.
- [ ] Literature on sensorimotor contingencies (O'Regan, Philipona) and developmental robotics (motor babbling).
- [ ] Neural Jacobian Fields, not re-read.
- [ ] Full text of Self-Upgrading Embodied Agents (abstract only) and Sections 2.2 onwards of SEAR (read only through a model summary).
- [ ] Octopus Protocol: test whether its pipeline can be combined with experiment-based identification of channels.

## Sources

Read (full text or large extract):

- [KnowBody, arXiv 2609.28530](https://arxiv.org/html/2609.28530v1)
- [RAX, arXiv 2610.22496](https://arxiv.org/html/2610.22496)
- [Act-Observe-Rewrite, arXiv 2603.04466](https://arxiv.org/html/2603.04466)
- [RACAS, arXiv 2603.05621](https://arxiv.org/html/2603.05621v2)
- [iAm.md, arXiv 2610.10962](https://arxiv.org/html/2610.10962v1)
- [Sensorimotor self-recognition, arXiv 2505.19237](https://arxiv.org/html/2505.19237v1)
- [Robust Visual Embodiment, arXiv 2510.03677](https://arxiv.org/html/2510.03677v1)
- [Meta-Harness, arXiv 2603.28052](https://arxiv.org/html/2603.28052v1)
- [HyperAgents, arXiv 2603.19461](https://arxiv.org/pdf/2603.19461)
- [LLM-IDEA, arXiv 2610.11253](https://arxiv.org/html/2610.11253v1)
- [ASIA, arXiv 2605.10480](https://arxiv.org/html/2605.10480)
- [FAEA, arXiv 2601.20334](https://arxiv.org/html/2601.20334v1)
- [When Robots Sleep, arXiv 2606.17493](https://arxiv.org/pdf/2606.17493)
- [Let Them Sleep, arXiv 2610.25561](https://arxiv.org/pdf/2610.25561)

Partially read (README or abstract):

- [HexaShell, repository](https://github.com/HexaFuture/HexaShell) and [arXiv abstract 2610.23479](https://arxiv.org/abs/2610.23479)
- [EAISys, repository](https://github.com/Interactive-Active-AI/EAISys)
- [Pierce and Kuipers 1997](https://web.eecs.umich.edu/~kuipers/research/pubs/Pierce-aij-97.html)
- [Hu and Lipson, arXiv 2311.12151](https://arxiv.org/abs/2311.12151v2)
- [robot-llm, repository](https://github.com/Jawbreaker1/robot-llm): excluded, the EV3 body is hand-coded and the model only chooses the route.

Cited without reading: [Bongard et al. 2006](https://static.ias.edu/pitp/archive/2012files/Resilient_Machines%28Science06%29.pdf), Neural Jacobian Fields.

Added after the extension to the OS objective and internal senses (read, some truncated): [PhyAgentOS](https://arxiv.org/abs/2607.16636), [HarnessPAI](https://arxiv.org/pdf/2609.29166), [Zetta](https://arxiv.org/html/2608.16590v1), [EmbodiedRSI](https://arxiv.org/pdf/2610.10498), [Embodied-Harness](https://arxiv.org/abs/2611.27689), [SHAPER](https://arxiv.org/abs/2608.11350), [rosaOS](https://aclanthology.org/2026.acl-demo.47/), [Interoceptive machine framework](https://arxiv.org/pdf/2604.24527), [INTERO](https://ceur-ws.org/Vol-4169/paper6.pdf), [Life-inspired interoceptive AI](https://arxiv.org/pdf/2309.05999v2), [Chen et al. 2026](https://arxiv.org/html/2606.13222v1), [Jiang et al. 2024, abstract](https://arxiv.org/abs/2402.18675), [Stovold et al. 2018](https://arxiv.org/pdf/1811.10033).
