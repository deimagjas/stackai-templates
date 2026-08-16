# Bugfix

This flow applies when fixing a defect in existing behavior. It starts by
proving the bug exists through a failing regression test, applies the
smallest change that makes it pass, and then confirms nothing else broke
by running the full computational sensor suite.

```mermaid
flowchart TD
    Start([Start: bug report]) --> WriteRegressionTest[Write a regression test\nthat reproduces the bug]
    WriteRegressionTest --> ConfirmRed[Confirm the test fails: red]
    ConfirmRed --> ApplyFix[Apply the minimal fix]
    ApplyFix --> ConfirmGreen[Confirm the test passes: green]
    ConfirmGreen --> Ruff[ruff]
    Ruff --> Ty[ty]
    Ty --> Tach[tach]
    Tach --> Pytest[pytest + coverage]
    Pytest --> CrapSensor[crap-sensor]
    CrapSensor --> Done([Bugfix considered done])

    class WriteRegressionTest,ConfirmRed,ApplyFix,ConfirmGreen computational
    class Ruff,Ty,Tach,Pytest,CrapSensor computational

    classDef computational fill:#cfe8ff,stroke:#2b6cb0,stroke-width:1px;
    classDef inferential fill:#ffd6ec,stroke:#b83280,stroke-width:1px;
```
