# Harness decision protocol — visual flows

This folder is the visual counterpart of the "decision protocol" that
governs which TDD/sensor order to follow depending on the kind of change
being made. It exists so that both humans onboarding to a template and
agents working inside one can see, at a glance, "what do I run and in what
order" without reading prose end to end.

The diagrams are drawn from the concrete toolchain of the
`python-cli-hexagonal` template today (ruff, ty, tach, pytest+coverage, a
crap-sensor, mutmut, and the adversarial-review skill), but the folder
itself — and the vocabulary it uses — is meant to generalize to future
templates. New templates should be able to add their own `flows/*.md`
files here using the same conventions, even if their concrete tools
differ.

## Vocabulary

The terms **harness**, **feedforward guide**, **feedback sensor**,
**computational sensor**, and **inferential sensor** come from the
Bockeler/Martin terminology used across this repository. They are defined
in [`../../AGENTS.md`](../../AGENTS.md) at the repo root — read that first
if any of these terms are unfamiliar. In short:

- A **feedforward guide** tells you what to do *before* you act (a plan,
  a decision protocol, a checklist).
- A **feedback sensor** tells you whether what you already did was
  correct, *after* the fact.
- A **computational sensor** is a feedback sensor whose verdict is
  produced by deterministic computation — a linter, a type checker, a
  dependency-boundary checker, a test runner, a coverage/complexity
  gate. Cheap, mechanical, no judgment involved.
- An **inferential sensor** is a feedback sensor whose verdict requires
  judgment — reading code and reasoning about it, the way a reviewer
  (human or LLM-driven) does. More expensive, catches what computation
  can't.

## What these diagrams are

Each file under [`flows/`](flows/) is the Mermaid flowchart form of a
decision protocol that otherwise lives as prose in:

- [`../../python-cli-hexagonal/.claude/skills/tdd-harness/SKILL.md`](../../python-cli-hexagonal/.claude/skills/tdd-harness/SKILL.md) —
  the TDD loop and the computational sensor suite (ruff, ty, tach,
  pytest+coverage, crap-sensor, mutmut).
- [`../../python-cli-hexagonal/.claude/skills/adversarial-review/SKILL.md`](../../python-cli-hexagonal/.claude/skills/adversarial-review/SKILL.md) —
  the inferential review step that closes out a change.

They are useful in two situations:

1. **Human onboarding.** A new contributor can see the whole decision
   protocol — which order to run things in, and why it differs by change
   type — as a picture, before diving into either SKILL.md.
2. **Agent context economy.** An agent that just needs "what's the order
   of operations for a bugfix" doesn't need to load a full skill into
   context; the flowchart alone answers that question.

These diagrams do not replace the SKILL.md files — they are a compressed,
visual index into the same protocol. When the two disagree, the SKILL.md
files are the source of truth.

## Flows

| File | Applies to |
| --- | --- |
| [`flows/new-feature.md`](flows/new-feature.md) | Implementing a new use case / feature |
| [`flows/bugfix.md`](flows/bugfix.md) | Fixing a bug |
| [`flows/refactor.md`](flows/refactor.md) | Refactoring without changing behavior |
| [`flows/new-adapter.md`](flows/new-adapter.md) | Adding a new adapter to an existing port |
| [`flows/architecture-change.md`](flows/architecture-change.md) | Changing module boundaries / layering |

## Mermaid styling convention

Every flowchart in this folder uses the same two `classDef`s to mark
whether a node is a computational sensor/step or an inferential one, so
the color coding is consistent across files and matches the convention
used by this repository's underlying knowledge base (blue = computational,
inferential = pink):

```mermaid
classDef computational fill:#cfe8ff,stroke:#2b6cb0,stroke-width:1px;
classDef inferential fill:#ffd6ec,stroke:#b83280,stroke-width:1px;
```

Applied per node as:

```mermaid
class NodeName computational
class NodeName inferential
```

- **Computational** nodes (blue, `fill:#cfe8ff stroke:#2b6cb0`): ruff, ty,
  tach, pytest+coverage, the crap-sensor, mutmut, and the TDD red/green
  steps themselves — anything whose verdict comes from running a
  deterministic tool.
- **Inferential** nodes (pink/magenta, `fill:#ffd6ec stroke:#b83280`):
  the adversarial-review skill, and any other step whose verdict requires
  judgment rather than computation.

Nodes that are neither a sensor nor a review step (plain actions like
"implement the adapter", or note/comment nodes) are left unstyled.
