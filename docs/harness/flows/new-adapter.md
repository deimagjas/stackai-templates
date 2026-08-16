# New adapter

This flow applies when adding a new adapter implementation for an
existing port (gateway), for example a new persistence backend or a new
notification channel. The port-contract test comes first because it is
what proves the new adapter honors the same behavioral contract as every
other adapter of that port, mirroring the pattern already established in
`tests/unit/test_port_contract.py` and backed by `ty`'s structural
(`Protocol`) checking at the wiring boundary.

```mermaid
flowchart TD
    Start([Start: new adapter for existing port]) --> PortContractTest[Write a port-contract test first,\nmirroring tests/unit/test_port_contract.py\nbacked by ty structural checking]
    PortContractTest --> ImplementAdapter[Implement the adapter]
    ImplementAdapter --> IntegrationTest[Write an integration test]
    IntegrationTest --> Done([New adapter considered done])

    class PortContractTest,ImplementAdapter,IntegrationTest computational

    classDef computational fill:#cfe8ff,stroke:#2b6cb0,stroke-width:1px;
    classDef inferential fill:#ffd6ec,stroke:#b83280,stroke-width:1px;
```
