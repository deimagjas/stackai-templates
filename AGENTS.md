# AGENTS.md — stackai-templates

This repository is a collection of AI-native project templates. Every
template ships with an explicit **harness** — the system of guides and
sensors that surrounds the coding agent — instead of leaving quality
control implicit in prose instructions or in the agent's judgment alone.
This file is the canonical, tool-agnostic contract for the whole
repository: it defines the vocabulary every template's own `AGENTS.md`
must use, and the structural rules every template must follow.

## Harness vocabulary

HARNESS VOCABULARY (use exactly this terminology, in English, as
technical terms even inside otherwise-Spanish prose):

- **Harness**: everything around the model in a coding agent. Canonical
  equation: `Agent = Model + Harness` (Birgitta Bockeler,
  martinfowler.com/articles/harness-engineering.html). Three layers: the
  model itself, the builder harness (what Claude Code ships out of the
  box: system prompt, tools, orchestration), and the user harness (what
  this repo adds on top).
- **Feedforward guide vs feedback sensor**: the horizontal axis.
  Feedforward guides steer the agent before it acts (AGENTS.md, skills,
  language servers, codemods). Feedback sensors observe the agent after
  it acts and let it self-correct (linters, type checkers, tests, review
  agents).
- **Computational sensor vs inferential sensor**: the mode axis, verbatim
  terms from Bockeler, "Maintainability sensors for coding agents"
  (martinfowler.com/articles/sensors-for-coding-agents.html).
  Computational sensors are deterministic, CPU-run, fast (linters, type
  checkers, test suites, mutation testing, dependency-cruiser-style
  checks). Inferential sensors are semantic, LLM-run, slower and
  non-deterministic but capable of judgment (AI code review, "LLM as
  judge"). NEVER use "linter" as the governing/umbrella term — a linter
  is one concrete instance of a computational sensor.
- **Sensor cadence** (Bockeler, 4 levels): during coding session
  (pre-commit, fast) -> after integration / pipeline (CI, reruns the
  fast ones + adds the expensive ones) -> repeatedly / drift (periodic,
  the harness "garbage collection") -> runtime (production monitoring).
- **Physical barriers** (Robert C. "Uncle Bob" Martin, Agentic
  Disciplines): a catalog of 7 immutable constraints, low to high
  abstraction: (1) Linter - basic syntax/style, (2) Unit tests / TDD
  (Three Laws) - bounding box for the agent behavior, (3) Coverage tool -
  forces the agent to cover what it left uncovered, (4) Acceptance tests
  in Gherkin (Given/When/Then) - THE LAW, immutable to the agent without
  explicit human approval, (5) CRAP metric -
  `CRAP(m) = complexity(m)^2 * (1 - coverage(m))^3 + complexity(m)`,
  threshold `<= 8`, forces small well-tested functions, (6) Mutation
  testing - semantic stability, catches behavior the agent changed
  without meaning to, (7) Dependency checker - enforces the Clean
  Architecture dependency rule (inner circles never import from outer
  circles). Key quote: "Physical barriers are not prompts, they are not
  things that you put into AGENTS.md. Physical barriers are tools that
  impose constraints upon what the AIs can do."
- **Operating rule**: use Bockeler's framework to CLASSIFY and ORGANIZE
  controls; use Uncle Bob's catalog as the non-negotiable CORE of the
  harness; never replace a physical barrier with a prompt. AGENTS.md and
  SKILL.md files SEQUENCE the barriers, they do not substitute for them.

## Contract for every template in this repo

Each template directory must contain:

1. Its own `AGENTS.md` documenting its concrete invariants, plus a
   **Harness Inventory** table mapping its actual tools to sensor type
   (computational / inferential), physical barrier (from the 7-item
   catalog above, if applicable), and cadence tier (session / pipeline /
   drift / runtime).
2. A thin `CLAUDE.md` whose entire first line is the literal text
   `@AGENTS.md` (Claude Code's documented @-import syntax: Claude Code
   expands this import at session load time, so Claude reads the shared
   `AGENTS.md` content plus any Claude-only lines after it, while other
   tools — Cursor, Windsurf, Cline, all of which read `AGENTS.md`
   natively as of mid-2026 — read `AGENTS.md` directly).
3. A Claude Code skill at `.claude/skills/<name>/SKILL.md` documenting
   the TDD/sensor sequencing protocol specific to that template.

## Adding a new harness

Checklist for supporting a future coding agent that does NOT read
`AGENTS.md` natively:

1. Create a thin pointer file at whatever path that tool expects,
   pointing at / importing `AGENTS.md`.
2. Never duplicate content — the pointer file must not restate rules,
   only redirect to them.
3. `AGENTS.md` stays the single source of truth. If the new tool's
   pointer syntax cannot express an import, keep the pointer file to the
   minimum needed to tell the agent to go read `AGENTS.md` first.

## Adding a new sensor

Generic checklist for adding a new computational or inferential sensor
to any template:

1. Register the tool in `pyproject.toml`/pre-commit/CI as appropriate
   for that template's stack.
2. Add a row to that template's Harness Inventory table (sensor type,
   physical barrier if any, cadence tier).
3. Decide its cadence tier explicitly: session, pipeline, drift, or
   runtime. Do not leave it implicit.
4. Update that template's `SKILL.md` with where the new sensor fits in
   the decision protocol — i.e., at what point in the TDD/sensor
   sequence the agent is expected to run it.

## Visual counterpart

`docs/harness/` at the repo root holds Mermaid flowcharts that are the
visual counterpart of each template's `SKILL.md` decision protocol.
They are useful for onboarding humans and for agents that want the flow
without loading a full skill.
