# Ipse

Ipse is a research project on robot self-improvement. It aims to propose a standard and an algorithm, in the manner of an operating system, that allow any robot to improve itself autonomously: the body is not described to the system, it is discovered by it.

## Status

The project is in a research phase. This repository contains no code: it gathers the framing documents, the literature review and, in due course, the specification of the standard.

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

## License

This repository is released under the Apache 2.0 license. See [LICENSE](LICENSE).
