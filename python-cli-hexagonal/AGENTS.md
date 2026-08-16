# Style and Architecture Rules (complement to ruff and tach)

## Harness Inventory

This file (`AGENTS.md`) is a **feedforward guide** — an inferential sensor: it steers the agent's behavior through convention and prior instruction, but it is not, by itself, a reliable physical barrier against violations. Only the tools listed below that fail with a compilable or runnable error (computational sensors) form the actual barrier that catches deviations mechanically, independent of whether the agent "read" or "understood" this document. For the real sequencing protocol in which these tools are run, see `.claude/skills/tdd-harness/SKILL.md`; for full definitions of the vocabulary used here (harness, feedforward guide, feedback sensor, computational sensor, inferential sensor), see the repo-root `AGENTS.md` (one level up, `../AGENTS.md`).

| Tool | Sensor type | Physical barrier | Cadence |
|---|---|---|---|
| ruff | computational | #1 Linter | session + pipeline |
| ty | computational | port-contract check | session + pipeline |
| pytest | computational | #2 Unit tests (TDD) | session + pipeline |
| pytest-cov | computational | #3 Coverage tool | session + pipeline |
| crap-sensor (external package, sibling repo) | computational | #5 CRAP metric | session + pipeline |
| mutmut | computational | #6 Mutation testing | periodic (CI cron/dispatch) |
| tach | computational | #7 Dependency checker | session + pipeline |
| adversarial-review skill (subagent) | inferential | review agent / QA Sentinel | session/pipeline, manual trigger |
| (future) Gherkin acceptance parser | computational | #4 Acceptance tests - THE LAW | session + pipeline |
| (future) adversarial-review wired into CI | inferential | AI Modularity Review equivalent | periodic (not built yet) |

This document collects the rules from the
[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
that `ruff` **cannot** enforce automatically, in addition to the
architectural invariants specific to this template.

What is automated lives in `pyproject.toml` (ruff) and in `tach.toml`
(boundaries). What follows must be respected manually and reviewed in
code review.

## 0. Conscious deviations from Google

- **Line length: 88** (Google = 80). We adopt the Black/ruff default
  for alignment with the modern ecosystem.
- **Indent: 4 spaces** (Google allows 2 or 4). PEP 8 and the default
  of the whole Python toolchain.

## 1. Hexagonal architecture (hard invariants)

These rules are **enforced by `tach check`**. They must not be relaxed:

- `app.domain` **never** imports from `app.adapters` or `app.entrypoint`.
- `app.domain.model` does not import from any other layer (not even
  the `app.domain` kernel).
- `app.domain.usecase` depends **only** on `app.domain.model` and the
  `app.domain` kernel; never the other way around (`model` does not
  know about `usecase`).
- `app.adapters` does not import from `app.entrypoint`.
- No circular dependencies between modules are allowed.
- A **new layer** at the top level under `src/app/` must be declared
  in `tach.toml` with its explicit `depends_on`. New features inside
  `model/` or `usecase/` do not require touching `tach.toml`.

Additional rules that are not automated:

- The **gateway (port) lives alongside its model** in
  `domain/model/<feature>/gateways.py`, not in a separate ports
  module.
- **Use cases are pure**: they receive the request and **return** a
  domain result. They **do not** perform IO (they do not call the
  port). Delivery happens in `entrypoint/`.
- **Feature-specific errors** live alongside their use case
  (`domain/usecase/<feature>/errors.py`) and inherit from
  `app.domain.errors.DomainError` (shared kernel).
- **The composition root is unique**: `wiring.build_dependencies` is
  the only place where adapters are instantiated; it is invoked once
  in the root callback of `entrypoint/cli.py` and injected via
  `ctx.obj`. Commands **do not** construct dependencies.
- External dependencies (typer, requests, sqlalchemy, etc.) live only
  in `adapters/` or `entrypoint/`, **never** in `domain/`.
- Test fakes/mocks live in `tests/conftest.py` or in files under
  `tests/`, **never** in `src/`.
- The mapping of domain exceptions to the output channel (exit
  codes, colors, formats) lives **only** in `entrypoint/cli.py`. The
  domain does not know about `typer.Exit`.

### Type checking (`ty`)

- The structural conformance of the adapters with their gateway's
  `Protocol` is verified by **`ty check`** (not `ruff` nor `tach`). It
  is part of the mandatory toolchain (pre-commit + CI).
- The conformance anchor is `wiring.py`: each adapter is returned
  typed as its port, so that `ty` detects any signature divergence
  before runtime.

## 2. Prohibited power features (Google §2.19)

- Do not use metaclasses unless there is explicit architectural
  justification.
- Do not use dynamic reflection (`getattr`/`setattr` with strings
  derived from external input) without a comment justifying it.
- Do not monkey-patch third-party modules.
- Do not use import hooks or manipulate `sys.modules`.

## 3. Threading and concurrency (Google §2.17)

- Do not introduce `threading`/`multiprocessing` without
  justification documented in the PR.
- Prefer `concurrent.futures` or `asyncio` over bare
  `threading.Thread`.
- Shared structures: use `queue.Queue` or thread-safe equivalents.

## 4. Docstrings (Google §3.8)

`ruff` with `convention = "google"` covers format and sections, but
these rules are qualitative:

- Modules: at least a one-line docstring.
- Public classes: docstring with an `Attributes:` section when
  applicable.
- Public functions: `Args:`, `Returns:`, `Raises:` sections when
  applicable.
- Private functions (`_foo`): may omit sections but must keep a
  summary.
- **Do not** document types in the docstring if they are already in
  the annotation.

## 5. Comments (Google §3.8.5)

- TODOs always with an author: `# TODO(username): description of
  what's missing`.
- Comments in complete sentences, with an initial capital letter and
  a final period.
- This template uses **Spanish** by the author's preference; keep
  consistency within the project.

## 6. Exceptions (Google §2.4)

- Every custom exception inherits from
  `app.domain.errors.DomainError`.
- A bare `except:` is prohibited (`ruff BLE001` blocks it, but this
  also applies to an unjustified `except Exception:`).
- Do not use exceptions for normal control flow.
- The `DomainError → typer.Exit` mapping lives **only** in
  `entrypoint/cli.py`.

## 7. Mutable global state (Google §2.5)

- Prohibited. Every dependency arrives via injection (ports +
  wiring).
- Constants in `UPPER_CASE` are acceptable if they are immutable.

## 8. Nested classes / inner functions (Google §2.16)

- Avoid nested classes except for clear factory patterns.
- Closures only when they capture relevant state; otherwise, move to
  top level.

## 9. Properties (Google §2.15)

- `@property` only for O(1) access with no observable side effects.
- If the property can fail or is expensive, use an explicit
  `get_*()` method.

## 10. Default mutable arguments (Google §2.12)

- `ruff B006` blocks it, but as a reminder: use `None` as a sentinel
  and build the default inside the function body.

## 11. Lambdas (Google §2.10)

- Only for one-line callbacks passed to `sorted`, `map`, etc.
- Never assign a lambda to a name (use `def`). Covered by `E731`.

## 12. Conditional expressions (Google §2.11)

- A single ternary expression per line. Nested ones → use
  `if`/`else`.

## 13. Imports (Google §2.13)

- Always absolute (`ruff TID252` configured).
- Order: stdlib, third-party, local (managed by `I`).
- One import per line.

## 14. Type annotations (Google §2.21)

- Mandatory on every public function and public class attributes
  (`ruff ANN`).
- `Any` only in justified dynamic interfaces (`ANN401` in `ignore`).
- Prefer `typing.Protocol` over ABCs for ports.

## 15. Long functions (Google §3.18)

- If a function exceeds ~40 lines, consider splitting it. `ruff
  PLR0915` gives a signal but doesn't cover every case; review in
  code review.

## 16. Logging (Google §2.18)

- `print()` is prohibited in production code (`ruff T201`).
- All user-facing output goes through an adapter (e.g.,
  `ConsoleGreeter`).
- For internal logs: `logging.getLogger(__name__)` with lazy
  formatting: `logger.info("user %s", user_id)`. f-strings inside log
  calls are blocked by `ruff G004`.

## 17. Naming (Google §3.16)

`ruff N` covers most of it. Conventions:

- `module_name`, `package_name`
- `ClassName`, `ExceptionName`
- `function_name`, `method_name`
- `GLOBAL_CONSTANT_NAME`
- `global_var_name`, `instance_var_name`, `function_parameter_name`,
  `local_var_name`
- "Internal": `_` prefix. Internal modules: `_` prefix in the file
  name.

## 18. Architecture evolution policy

When adding a new use case or adapter:

1. Follow the steps in "How to add a new command" from the README.
2. New features inside `domain/model/` or `domain/usecase/` do not
   require touching `tach.toml` (they belong to an already declared
   layer). Only if a **new** top-level layer is introduced under
   `src/app/` does it need to be registered with its explicit
   `depends_on`.
3. **Never** invert the layer flow: `model` does not depend on
   `usecase`, and `domain` does not depend on `adapters` or
   `entrypoint`. That is the invariant that protects the
   architecture.
