# Architecture change

This flow applies when changing module boundaries or layering itself —
for example adding a new top-level layer under `src/app/` or altering
which layers may depend on which. Unlike the other flows, the
computational sensor for structure (`tach check`) runs *before* any code
is written, as an upfront guardrail that confirms the intended boundary
change is actually expressible, rather than only as a final check.

```mermaid
flowchart TD
    Start([Start: architecture change]) --> TachUpfront[Run tach check upfront,\nas a guardrail before writing code]
    TachUpfront --> Guardrail{Boundary change\nis expressible?}
    Guardrail -- No --> Reconsider[Reconsider the boundary change]
    Reconsider --> TachUpfront
    Guardrail -- Yes --> MakeChange[Make the change]
    MakeChange --> Ruff[ruff]
    Ruff --> Ty[ty]
    Ty --> TachAgain[tach, again]
    TachAgain --> Pytest[pytest + coverage]
    Pytest --> CrapSensor[crap-sensor]
    CrapSensor --> Done([Architecture change considered done])

    class TachUpfront,Ruff,Ty,TachAgain,Pytest,CrapSensor computational

    classDef computational fill:#cfe8ff,stroke:#2b6cb0,stroke-width:1px;
    classDef inferential fill:#ffd6ec,stroke:#b83280,stroke-width:1px;
```
