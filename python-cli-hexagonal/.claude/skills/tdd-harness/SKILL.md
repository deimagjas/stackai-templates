---
name: tdd-harness
description: This skill triggers whenever the agent is about to implement a new use case or feature, fix a bug, refactor existing code, add a new adapter, or change the architecture/dependency boundaries in this template. It teaches the specific order in which this template's computational and inferential sensors must be run for each of those change types — that order is NOT the same for every kind of change, and running sensors out of order (or skipping the cheap ones first) wastes cycles and lets defects slip through.
---

# TDD Harness — sequencing the sensors

## Vocabulary recap

This template follows a **harness** (Kent Beck / Birgitta Böckeler framing):
the model (the code the agent writes) plus the harness (the guides and
sensors around it). A **feedforward guide** (this file, `AGENTS.md`) tells
the agent what to do *before* it acts; a **feedback sensor** tells it,
after acting, whether it actually worked. Sensors split into
**computational sensors** (deterministic, run by a compiler/interpreter —
ruff, ty, pytest, tach) and **inferential sensors** (judgment calls made by
another model — the adversarial-review skill). Never call either kind a
"linter" — that collapses a distinction the rest of this harness depends
on. Full definitions live in
[`../../../AGENTS.md`](../../../AGENTS.md) (this template) and in the
repo-root [`../../../../AGENTS.md`](../../../../AGENTS.md) (tool-agnostic
theory for every template in this repo). This skill does not repeat that
theory — it only sequences the sensors it defines.

## Sensor inventory of this template

| Sensor | Kind | Checks |
|---|---|---|
| `ruff` | computational | lint + format, Google style subset |
| `ty` | computational | types + structural port conformance (adapter vs `Protocol`) |
| `tach` | computational | architecture/dependency boundaries (`domain` never imports `adapters`/`entrypoint`) |
| `pytest` (+ `pytest-cov`) | computational | behavior, via unit + integration tests |
| `crap-sensor` | computational | Change Risk Anti-Patterns score per function/module (complexity × uncovered risk) |
| `mutmut` | computational | mutation testing — do the tests actually kill mutants, or just execute lines |
| adversarial-review skill | inferential | a second agent tries to *refute* the change: architecture drift, missed edge cases, semantic drift |
| Gherkin acceptance tests *(future)* | computational | barrier #4, not yet built — see "Extending the harness" |
| adversarial-review in CI *(future)* | inferential | wiring the skill into CI on a periodic cadence — not yet built |

See `AGENTS.md` (template) for the full table with columns for cadence,
command, and failure mode.

## Decision protocol — the order depends on the change type

The five cases below are the change types this skill covers. Pick the one
that matches, and run the steps **in that exact order** — do not jump to
the expensive sensors before the cheap ones have passed, and do not skip
a step because a later one "would probably catch it too."

### 1. New use case / feature

Diagram: [`../../../../docs/harness/flows/new-feature.md`](../../../../docs/harness/flows/new-feature.md)

1. Apply the **Three Laws of TDD** *inside* `domain/usecase/<feature>/`,
   against a **fake gateway** (the pattern in `tests/conftest.py`):
   write a failing test → write the minimal code to pass it → refactor →
   loop. Do not touch a real adapter yet.
2. Implement the real adapter in `adapters/` once the use case is proven
   against the fake.
3. Run the full sensor suite, cheapest first:
   `ruff` → `ty` → `tach` → `pytest` (with coverage) → `crap-sensor`.
4. Invoke the **adversarial-review** skill before calling the feature
   done. Do not skip this step because the sensors above are green — it
   catches what they structurally cannot.

### 2. Bug fix

Diagram: [`../../../../docs/harness/flows/bugfix.md`](../../../../docs/harness/flows/bugfix.md)

1. Write a **failing regression test** that reproduces the bug first.
   Run it and confirm it is red — a bug fix without a preceding red test
   is unverified.
2. Write the **minimal fix**.
3. Confirm the regression test is now green.
4. Run the full sensor suite (same order as above:
   `ruff` → `ty` → `tach` → `pytest`+coverage → `crap-sensor`).

### 3. Refactor with no behavior change

Diagram: [`../../../../docs/harness/flows/refactor.md`](../../../../docs/harness/flows/refactor.md)

1. Run the sensors **first**, before touching anything, to establish a
   green baseline.
2. Refactor.
3. Run the sensors **again** — they must stay green. Do **not** add new
   tests unless the observable surface changed (if it did, this was not
   a pure refactor — treat it as case 1 or 2 instead).
4. `mutmut` runs on a periodic cadence (CI), not required locally for a
   refactor — do not block on it here.

### 4. New adapter

Diagram: [`../../../../docs/harness/flows/new-adapter.md`](../../../../docs/harness/flows/new-adapter.md)

1. Write the **port-contract test first**, following the pattern in
   `tests/unit/test_port_contract.py` (a static anchor typed as the
   port, checked by `ty`, plus a runtime `isinstance` check against the
   `Protocol`).
2. Run `ty` — it must fail against the not-yet-implemented adapter.
3. Implement the adapter until the contract test and `ty` both pass.
4. Add an **integration test** exercising the adapter through the real
   composition root (`wiring.build_dependencies`), not just the fake.

### 5. Architecture / dependency-boundary change

Diagram: [`../../../../docs/harness/flows/architecture-change.md`](../../../../docs/harness/flows/architecture-change.md)

1. Run `tach check` **before writing any code** — as an upfront
   guardrail that tells you whether the boundary change you are about to
   make is even representable in `tach.toml`, not just as a final check.
2. Make the change (code + `tach.toml` if a new top-level layer under
   `src/app/` is being introduced).
3. Run `tach check` again, then the rest of the sensor suite.

## Reliability note

Robert C. Martin's point applies directly here: this `SKILL.md` and
`AGENTS.md` are **feedforward, inferential guidance** — instructions a
model reads and may or may not follow correctly. They are not reliable by
themselves. The only things that constitute a real barrier are
**computational sensors that fail with a compilable/runnable error**
(`ruff`, `ty`, `tach`, `pytest`, `crap-sensor`, `mutmut`). This skill's job
is to **sequence** those barriers correctly for the change at hand — it
does not replace them, and reading it is not a substitute for actually
running the sensors it names.

The one inferential sensor in this template, **adversarial-review**, is an
*amplifier* on top of the computational barriers — it catches things
compilers and test runners structurally cannot (architectural drift,
missing edge cases, semantic mismatches). It is never a substitute for
them: a change that fails `ruff`/`ty`/`tach`/`pytest` is not done no matter
what an adversarial review says about it.

## Extending the harness

If you need to add a new sensor to this template (a new computational
check, or wiring an existing one into CI), follow the **"Adding a new
sensor"** checklist in the repo-root
[`../../../../AGENTS.md`](../../../../AGENTS.md). Two extensions are
already documented there but not yet built:

- **Gherkin acceptance tests** as barrier #4 (behavior specified in
  Gherkin, executed as a computational sensor).
- **Wiring `adversarial-review` into CI** on a periodic cadence, rather
  than only running it locally before marking a feature done.

Do not build either of these as part of following this skill — they are
tracked separately in the repo-root checklist.
