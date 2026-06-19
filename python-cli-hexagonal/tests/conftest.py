"""Fixtures compartidas para tests."""

from dataclasses import dataclass, field

import pytest

from app.domain.model.greeting.gateways import GreeterPort
from app.domain.model.greeting.models import Greeting


@dataclass
class FakeGreeter:
    """Adapter en memoria; satisface estructuralmente `GreeterPort`."""

    delivered: list[Greeting] = field(default_factory=list)

    def deliver(self, greeting: Greeting) -> None:
        self.delivered.append(greeting)


# Ancla estatica de conformidad: `ty` verifica que `FakeGreeter` cumpla
# estructuralmente `GreeterPort` (incluida la firma de `deliver`), de modo
# que un fake desactualizado rompa el type-check, no solo el runtime. El
# adapter real ya queda anclado por `wiring.build_dependencies`.
_fake_conforms_to_port: GreeterPort = FakeGreeter()


@pytest.fixture
def fake_greeter() -> FakeGreeter:
    return FakeGreeter()
