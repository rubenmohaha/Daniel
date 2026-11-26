# Ipse

Ipse is a research project on robot self-improvement. It aims to propose a standard and an algorithm, in the manner of an operating system, that allow any robot to improve itself autonomously from a minimal contract: the body is not described to the system, it is discovered by it.

## Status

The project is in a research phase. This repository contains no code: it gathers the framing documents, the literature review and, in due course, the specification of the standard.

## Principles

- **The body is discovered, not described.** The robot exposes only anonymous motor channels, their bounds, and sensor streams. The system itself establishes the body description and the control interface.
- **A fixed foundation evaluates every version.** Self-improvement is bounded by a foundation that only a human may modify, which applies a veto (safety, honesty) before any scoring (reliability, performance).
- **A day/night cycle.** Learning happens during operation; rest simplifies the code, and a simplified version is adopted only if its behaviour is unchanged.
- **The same code on different bodies.** The success criterion is the discovery of two very different bodies without any code change, including recovery after motor cables are swapped.

## Documents

| Document | Content |
| --- | --- |
| [Framing note](docs/framing/framing-note.md) | Hypothesis, three-layer architecture, evaluation criteria, demonstration protocol, open questions |
| [Literature review](docs/literature-review/literature-review.md) | Closest related work, corrections made to the framing note, positioning, and remaining reading |

## License

This repository is released under the Apache 2.0 license. See [LICENSE](LICENSE).
