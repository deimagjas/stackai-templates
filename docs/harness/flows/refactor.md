# Refactor

This flow applies when restructuring existing code without changing its
observable behavior. The sensor suite runs twice — once before, to
establish a green baseline, and once after, to prove nothing changed
behaviorally — and no new tests are required unless the refactor actually
changed the observable surface (in which case it is no longer a pure
refactor and the new-feature or bugfix flow applies instead).

```mermaid
flowchart TD
    Start([Start: refactor]) --> BaselineSuite[Run sensor suite:\nruff, ty, tach, pytest+coverage, crap-sensor]
    BaselineSuite --> BaselineGreen{Baseline green?}
    BaselineGreen -- No --> FixFirst[Fix baseline before refactoring]
    FixFirst --> BaselineSuite
    BaselineGreen -- Yes --> Refactor[Refactor: no behavior change]
    Refactor --> RerunSuite[Run sensor suite again:\nruff, ty, tach, pytest+coverage, crap-sensor]
    RerunSuite --> StillGreen{Still green,\nno observable surface change?}
    StillGreen -- No --> Refactor
    StillGreen -- Yes --> Done([Refactor considered done])
    Done -.-> MutmutNote[["Note: mutmut (mutation testing) validates\nsemantic stability further, but it runs on a\nperiodic CI cadence — not required locally\nfor every refactor."]]

    class BaselineSuite,Refactor,RerunSuite computational

    classDef computational fill:#cfe8ff,stroke:#2b6cb0,stroke-width:1px;
    classDef inferential fill:#ffd6ec,stroke:#b83280,stroke-width:1px;
```
