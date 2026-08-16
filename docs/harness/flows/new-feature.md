# New feature / new use case

This flow applies when implementing a brand-new use case or feature in
the domain layer — the most common change. It starts with a Three Laws
of TDD loop written against the use case in isolation (with a fake
gateway standing in for the real adapter), moves on to the real adapter
implementation once the use case is proven, and then closes with the
full computational sensor suite run cheapest-first, followed by the one
inferential step: the adversarial-review skill.

```mermaid
flowchart TD
    Start([Start: new use case / feature]) --> WriteFailingTest[Write a failing unit test\nfor the use case, using a fake gateway]
    WriteFailingTest --> WriteMinimalCode[Write the minimal code\nto make it pass]
    WriteMinimalCode --> RefactorLoop[Refactor]
    RefactorLoop --> Complete{Use case complete?}
    Complete -- No --> WriteFailingTest
    Complete -- Yes --> RealAdapter[Implement the real adapter]
    RealAdapter --> Ruff[ruff]
    Ruff --> Ty[ty]
    Ty --> Tach[tach]
    Tach --> Pytest[pytest + coverage]
    Pytest --> CrapSensor[crap-sensor]
    CrapSensor --> AdversarialReview[adversarial-review skill]
    AdversarialReview --> Done([Feature considered done])

    class WriteFailingTest,WriteMinimalCode,RefactorLoop computational
    class RealAdapter,Ruff,Ty,Tach,Pytest,CrapSensor computational
    class AdversarialReview inferential

    classDef computational fill:#cfe8ff,stroke:#2b6cb0,stroke-width:1px;
    classDef inferential fill:#ffd6ec,stroke:#b83280,stroke-width:1px;
```
