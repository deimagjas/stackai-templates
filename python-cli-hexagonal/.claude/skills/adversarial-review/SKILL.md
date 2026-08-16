---
name: adversarial-review
description: This skill triggers when a feature or fix in this template is considered functionally done — after the computational sensors (ruff, ty, tach, pytest) are green — and before handing the change back to the human. It does NOT trigger automatically on every change or every file edit; it is a deliberate, on-demand step invoked once per unit of work when the agent believes it has finished.
---

# Adversarial Review

## Purpose

This skill operationalizes the **inferential sensor** described in
`AGENTS.md`: Böckeler's "review agent" / "LLM as judge" pattern, and Uncle
Bob's "QA Sentinel Agent" idea. The core problem it addresses is that the
agent that wrote the code is a biased reviewer of its own work — it
already believes its solution is correct, so asking it to re-check itself
tends to confirm rather than refute. This skill launches a **second
agent**, in a fresh context, whose explicit job is to try to **refute**
the change rather than approve it.

## How to invoke it

Use the Agent tool to launch a **subagent** — never do this "review" by
reasoning in the main session, since that reintroduces the same
self-confirmation bias this skill exists to counter. The prompt given to
the subagent must include:

1. **The diff / files touched** by the change under review.
2. **This template's invariants**, drawn from `AGENTS.md`:
   - the dependency rule (`domain` never imports `adapters` or
     `entrypoint`; `model` never imports `usecase`);
   - use cases must be pure (they return a domain result, they never
     perform IO themselves);
   - the composition root is single (`wiring.build_dependencies`,
     invoked once, in `entrypoint/cli.py`);
   - the gateway-next-to-model convention (a feature's port lives in
     `domain/model/<feature>/gateways.py`, not in a separate ports
     module).
3. An **explicit instruction to look for**:
   - architecture violations (even subtle ones `tach` cannot see, e.g. a
     use case reaching into an adapter's concrete type instead of its
     port);
   - uncovered edge cases (empty/None inputs, boundary values, error
     paths the tests do not exercise);
   - semantic drift (the code does something plausible-looking but
     different from what the request actually asked for).
4. An explicit instruction **not** to summarize or praise the change —
   the subagent's job is to find problems, not to write a changelog
   entry.

## What it produces

A list of findings, each with:

- a **severity**,
- the **file and line** it applies to,
- a **concrete scenario** that triggers the problem (input/state →
  wrong behavior), not a vague "this could be an issue."

## Explicit limits

Adversarial review is an **inferential sensor** — a judgment call by
another model, not a deterministic check. It **complements** the
computational sensors (`ruff`, `ty`, `tach`, `pytest`, `crap-sensor`,
`mutmut`); it never replaces them. Its findings are **suggestions** for
the human or the main agent to act on — they are not a blocking gate the
way a failing `tach check` or a failing test is. A change with clean
adversarial-review findings can still be wrong if a computational sensor
is failing; a change with adversarial-review findings still needs the
human or the main agent to decide which findings are worth acting on.

## Future extension

Wiring this skill into CI on a periodic cadence (an "AI Modularity
Review" style job, not on every PR) would require an `ANTHROPIC_API_KEY`
secret and headless execution of the subagent outside an interactive
session. That is out of scope for this skill today and is tracked in the
repo-root `AGENTS.md` checklists, alongside Gherkin acceptance tests as
barrier #4.
