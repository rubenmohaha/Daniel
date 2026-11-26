# Daniel

Daniel is a research project on robot self-improvement. It aims to propose a standard and an algorithm, in the manner of an operating system, that allow any robot to improve itself autonomously: the body is not described to the system, it is discovered by it.

## Status

The project is in a research phase. This repository gathers the framing documents, the literature review, the plan of the first prototype and its fixed part, and, in due course, the specification of the standard.

## Principles

- **The body is discovered, not described.** No human writes a description of the robot. The system may inventory what Linux reports, but nothing enters its body description without having been confirmed by experiment.
- **An adult mind in an unknown body.** The built-in language model already knows a great deal about the world; what it does not know is its own body. The mind does not grow: what grows is its written knowledge of its body and its know-how.
- **Three things are fixed.** Linux, a built-in language model, and a small set of instincts modelled on those of animals: hunger, temperature, sleep, pain, fear and curiosity.
- **Everything else evolves.** The body description, code, skills and memory are written by the model and can be rewritten by it. This is where self-improvement happens.
- **Humans communicate through the senses.** They do not intervene inside the system; they relate to it as a teacher does, through voice, hearing and other perceivable signals.
- **The same code on different bodies.** The success criterion is the discovery of two very different bodies without any code change, including recovery after motor cables are swapped.

## Documents

| Document | Content |
| --- | --- |
| [Framing note](docs/framing/framing-note.md) | Objective, fixed and evolving elements, instincts, body discovery, demonstration protocol, open questions |
| [Literature review](docs/literature-review/literature-review.md) | Closest related work, corrections made to the framing note, positioning, and remaining reading |
| [First prototype plan](docs/prototype/first-prototype-plan.md) | Fixed part written by the project, what Daniel writes, setup, first test, known limits and open questions |
| [Fixed part of the first prototype](fixed/README.md) | The loop, the starting instruction, Daniel's container, setup and tests |
| [Decision log](docs/decisions/decision-log.md) | Questions settled so far, with their date, reason and the earlier choices they replace |

## Installing the first prototype

From any computer with SSH, where `USER@ROBOT` is the account and address of a robot running Linux:

```
ssh -t USER@ROBOT "curl -fsSLo daniel.sh github.com/rubenmohaha/Daniel/raw/main/install.sh && sudo bash daniel.sh"
```

See [the fixed part](fixed/README.md) for what this command does.

## License

Copyright 2026 Ruben Moha. This repository is released under the Apache 2.0 license. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
