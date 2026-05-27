"""Fixtures compartidas para tests."""

from dataclasses import dataclass, field

import pytest

from app.domain.models import Greeting


@dataclass
class FakeGreeter:
    """Adapter en memoria; satisface estructuralmente `GreeterPort`."""

    delivered: list[Greeting] = field(default_factory=list)

    def deliver(self, greeting: Greeting) -> None:
        self.delivered.append(greeting)


@pytest.fixture
def fake_greeter() -> FakeGreeter:
    return FakeGreeter()
