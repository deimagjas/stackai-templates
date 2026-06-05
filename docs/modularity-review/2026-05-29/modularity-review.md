# Modularity Review

**Scope**: `python-cli-hexagonal` template — entire codebase (`domain/`, `adapters/`, `entrypoint/`, wiring, and the test doubles that integrate with the ports)
**Date**: 2026-05-29

## Executive Summary

`python-cli-hexagonal` is a copy-and-extend **template** for building Typer-based command-line tools with a hexagonal (ports & adapters) layout. Its real deliverable is not the bundled `greet` example — that is a placeholder — but the *structure and its guardrails*: the `domain → adapters → entrypoint` dependency direction enforced by `tach`, the `Protocol`-based ports, and the documented recipe for adding new commands. As a piece of [modular design](https://coupling.dev/posts/core-concepts/modularity/), the template is largely **healthy**: integration strength is deliberately kept low (frozen dataclasses and a structural `Protocol`), distance is low (one package, one process), and the example's volatility is negligible, so most integrations are [balanced](https://coupling.dev/posts/core-concepts/balance/) by construction. The most important finding is that the template's central promise — that adapters conform to domain ports — relies on [contract coupling](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) that **no tool in the toolchain actually verifies**: `tach` checks import direction, `ruff` checks style, `pytest` checks the one example's behavior, but nothing checks that an adapter satisfies its port. Because adding ports and adapters is exactly what adopters do most, that unverified contract sits in the template's highest-[volatility](https://coupling.dev/posts/dimensions-of-coupling/volatility/) area.

## Coupling Overview

| Integration | [Strength](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) | [Distance](https://coupling.dev/posts/dimensions-of-coupling/distance/) | [Volatility](https://coupling.dev/posts/dimensions-of-coupling/volatility/) | [Balanced?](https://coupling.dev/posts/core-concepts/balance/) |
| ----------- | ----------- | -------- | ---------- | --------- |
| `adapters.ConsoleGreeter` → `domain.ports.GreeterPort` (structural conformance) | [Contract](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) — but **implicit / unenforced** | Cross-module, same package/process | **High** (adopters add ports & adapters constantly) | ⚠️ **No** — implicit coupling in a volatile area |
| `tests.FakeGreeter` → `domain.ports.GreeterPort` (structural conformance) | [Contract](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) — implicit / unenforced | Cross-module (tests ↔ src) | **High** | ⚠️ **No** — same root cause as above |
| `entrypoint.commands.greet` → `entrypoint.wiring.build_greeter` | [Functional](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) — command performs its own composition | Same package | Moderate (grows with every new command) | ⚠️ **Partial** — composition concern scatters as commands multiply |
| `domain.use_cases.greet` → `domain.ports.GreeterPort` (`deliver` side effect) | [Functional](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) — computation + I/O orchestration fused | Same module | Low (for the example) | ▲ Balanced today; pattern risk at scale |
| `entrypoint.commands.greet` → `domain.use_cases` / `domain.models` | [Model](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) — shares `GreetingRequest`/`Greeting` | Cross-module, same process | Moderate | ✅ Balanced |
| `entrypoint.wiring.build_greeter` → `adapters.ConsoleGreeter` | [Model](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) — constructs concrete, returns as port | Cross-module | Low | ✅ Balanced (correct dependency inversion) |
| `entrypoint.cli.main` → `domain.errors.DomainError` (catch-all → exit 1) | [Contract](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) — base-class catch only | Cross-module | Low | ✅ Balanced (mapping isolated to one place) |

The last three rows are the template doing its job well and are recorded for completeness; the issues below cover the three flagged rows.

## Issue: The port↔adapter contract is implicit and unverified by the toolchain

**Integration**: `adapters.ConsoleGreeter` (and `tests.FakeGreeter`) → `domain.ports.GreeterPort`
**Severity**: Significant

### Knowledge Leakage

The whole point of a `typing.Protocol` port is to make the integration a *explicit* [contract](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/): the domain publishes `GreeterPort.deliver(self, greeting: Greeting) -> None`, and adapters conform structurally without inheriting. In principle this is the weakest, most desirable form of [integration strength](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/).

The problem is *enforcement*. Structural conformance is asserted nowhere a machine can see it. `ConsoleGreeter` never references `GreeterPort`; `wiring.build_greeter()` returns it under the `GreeterPort` annotation, but no type checker runs against that site. The dev dependencies (`ruff`, `pytest`, `pytest-cov`, `tach`, `pre-commit`) contain **no type checker** (no `mypy`, `pyright`, or `ty`); CI runs `ruff check`, `ruff format --check`, `tach check`, `pytest`; pre-commit runs `ruff` + `tach`. `tach` enforces *import direction* (`domain` may not import `adapters`), not *type conformance*. The result: a contract that *looks* explicit is in practice **implicit** — its satisfaction is a human promise. Implicit coupling that should be explicit is the dangerous kind, because the integration point is invisible until it breaks at runtime.

### Complexity Impact

Implicit coupling makes change outcomes unpredictable, which is the definition of [complexity](https://coupling.dev/posts/core-concepts/complexity/). When the shared knowledge (the port signature) is not machine-checked, a developer editing the port has no signal telling them which adapters and test doubles must move in lockstep. They must hold the full set of conformers in their head — and the working-memory budget of 4±1 items is exhausted the moment a real project has a handful of ports each with two or three adapters plus fakes. The template *teaches* a pattern whose safety net is missing, so every project cloned from it inherits the blind spot.

### Cascading Changes

- A developer renames `deliver` to `emit`, or changes its signature to `deliver(self, greeting: Greeting, *, stream) -> None`. `ConsoleGreeter` and `FakeGreeter` still *parse* and still *import-check* under `tach`. The unit tests pass (they call the fake directly), and the break only surfaces when the real CLI path executes the stale adapter at runtime — an `AttributeError`/`TypeError` discovered in production rather than in CI.
- An adopter adds a second adapter (`LoggingGreeter`) and forgets one method, or gets an argument name wrong. Nothing fails until that adapter is wired and invoked.

Because the integration lives in the template's **highest-volatility** region — adding ports/adapters is the primary growth activity under "varies widely" adoption — these silent breaks are not rare edge cases; they are the expected failure mode of the template's day-to-day use.

### Recommended Improvement

Make the existing contract *explicit to tooling* rather than changing the design — the [strength](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) is already where you want it; only its verification is missing.

1. Add a static type checker (`ty`, `mypy`, or `pyright`) to the dev dependencies, the pre-commit hooks, and the CI workflow, configured to check `src/` *and* `tests/`. This turns structural conformance into a checked, build-breaking contract — closing the gap without raising strength or distance.
2. Optionally, add one assertion site that pins the relationship the type checker keys on — e.g. in `wiring.py` the return is already annotated `-> GreeterPort`, so a checker will flag a non-conforming `ConsoleGreeter` there. Document in the "how to add a command" recipe that *every* adapter must be returned through a `GreeterPort`-annotated factory so the checker has an anchor.

**Trade-off**: a type checker adds a CI step, some annotation discipline, and occasional friction with dynamic code. For a template that markets itself on ports & adapters correctness, that cost is plainly worth it — without it, the headline feature is unguarded precisely where adopters lean on it hardest.

## Issue: Composition is performed inside commands, fragmenting the composition root

**Integration**: `entrypoint.commands.greet.run` → `entrypoint.wiring.build_greeter`
**Severity**: Significant

### Knowledge Leakage

`wiring.py`'s own docstring states its purpose: *"Centralizar el wiring aqui permite cambiar adapters … modificando un unico archivo."* But the *selection and construction* of the adapter happens inside `greet.run()`, which calls `build_greeter()` itself. The command therefore carries [functional](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) knowledge — "to greet, you assemble a greeter" — that the design intends to keep in the composition root. Step 6 of the README recipe instructs every new command to call its own `build_*()` inside `run()`, so this is a *prescribed* pattern, not a one-off.

### Complexity Impact

For a single command the duplication is invisible. The cost appears as commands multiply: the composition root is no longer a place, it is a scattering of `build_*()` calls across N command modules. Any cross-cutting change to *how* dependencies are assembled (environment-based adapter selection, swapping in test doubles at the boundary, threading a shared resource like an HTTP client or DB session through several commands) must be reasoned about across every command file rather than in one root — exceeding the cognitive budget the centralized-wiring design was meant to protect. This is [low cohesion](https://coupling.dev/posts/core-concepts/balance/) of the composition concern: a single responsibility (object assembly) smeared across many low-volatility command modules.

### Cascading Changes

- Adopter wants all commands to use a `LoggingGreeter` in one environment and `ConsoleGreeter` in another. With composition inlined per command, the conditional must be added to (or imported into) each command, or each `build_*` must grow environment logic. With a true root, it is one change.
- Adopter wants integration tests to inject fakes at the composition boundary instead of monkeypatching. Today there is no single seam to inject at — each command reaches into `wiring` on its own.

The distance between the scattered call sites is low (same package), so the changes are not *expensive* per file — but they are *many* and *repetitive*, which is exactly the drift toward a [big ball of mud](https://coupling.dev/posts/core-concepts/balance/) that low cohesion produces.

### Recommended Improvement

Keep `wiring.py` as the composition root and stop commands from constructing their own dependencies. Two viable shapes:

- **Inject the port into the command**: have `cli.py` (the true root) build the greeter via `wiring` and pass it to `run(greeter, name=...)`, so the command receives its collaborators rather than fetching them. Distance and strength stay low; the composition concern returns to one place.
- **Or** make `wiring.py` expose a single `build_dependencies()`/container that `cli.py` assembles once at startup and hands to commands.

**Trade-off**: Typer commands receiving injected dependencies need a small amount of plumbing (a partial, a closure, or a context object) because Typer wants to own the callback signature. That is a modest, one-time cost in the template's `cli.py`, paid back every time an adopter adds a command or needs an environment-specific or test wiring — and it makes the template's stated "single file to swap adapters" promise actually true.

## Issue: Use cases fuse pure computation with output delivery

**Integration**: `domain.use_cases.greet` → `domain.ports.GreeterPort.deliver`
**Severity**: Minor

### Knowledge Leakage

`greet()` both *computes* the result (`Greeting(message=f"Hola, {name}!")`) and *performs the side effect* (`greeter.deliver(greeting)`) before returning. The pure transformation and the I/O orchestration are [functionally coupled](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) inside one function. A use case can no longer be evaluated for its result without also triggering delivery through whatever port is supplied.

### Complexity Impact

At the current size this is fully [balanced](https://coupling.dev/posts/core-concepts/balance/) — the distance is a single module and the example's volatility is negligible. The concern is that, as the *documented pattern of the template*, it pushes output orchestration into the domain. A use case that wants to call another use case inherits its delivery side effect; composing two domain operations forces a decision about which deliveries fire. That is how I/O responsibilities accrete in a layer that is supposed to stay pure and composable.

### Cascading Changes

- An adopter adds a `report` use case that internally needs `greet`'s computed message but should emit it through a *different* channel (a file, an aggregated report). Today they cannot reuse `greet` without also triggering its `deliver`; they must duplicate the message-building logic or refactor the side effect out under pressure.

### Recommended Improvement

This is a *pattern* recommendation for the template, not an urgent fix to the example. Consider establishing the convention that **use cases return domain results and the entrypoint performs delivery** — i.e. `greet()` returns `Greeting`, and `commands/greet.py` (or the injected port from the previous issue) calls `deliver`. Keep `deliver`-from-use-case available where a use case genuinely orchestrates streaming/long-running output, but make "compute, return, let the edge render" the default the recipe teaches.

**Trade-off**: moving delivery to the edge means the entrypoint, not the use case, owns the "and then show it" step — a slightly thicker command layer. Given that the template's purpose is to model clean separation for arbitrary adopters, teaching composable pure use cases is worth that small shift. Because the imbalance is low-volatility today, this can be addressed opportunistically rather than urgently.

---

_This analysis was performed using the [Balanced Coupling](https://coupling.dev) model by [Vlad Khononov](https://vladikk.com)._
