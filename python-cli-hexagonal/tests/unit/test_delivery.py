"""Test del patron de entrega via el `GreeterPort` con un fake adapter.

El caso de uso ya no entrega el saludo (es puro); la entrega ocurre en el
borde. Este test ejercita ese contrato con `FakeGreeter`.
"""

from app.domain.model.greeting.models import GreetingRequest
from app.domain.usecase.greet.use_case import greet


def test_greeting_is_delivered_through_port(fake_greeter):
    greeting = greet(GreetingRequest(name="Ada"))

    fake_greeter.deliver(greeting)

    assert fake_greeter.delivered == [greeting]
