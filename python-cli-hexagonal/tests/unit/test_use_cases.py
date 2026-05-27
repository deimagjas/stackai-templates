"""Tests unitarios del use case `greet` con un fake adapter."""

import pytest

from app.domain.errors import EmptyNameError
from app.domain.models import GreetingRequest
from app.domain.use_cases import greet


def test_greet_delivers_message(fake_greeter):
    result = greet(GreetingRequest(name="Ada"), fake_greeter)

    assert result.message == "Hola, Ada!"
    assert len(fake_greeter.delivered) == 1
    assert fake_greeter.delivered[0].message == "Hola, Ada!"


def test_greet_trims_whitespace(fake_greeter):
    result = greet(GreetingRequest(name="  Ada  "), fake_greeter)
    assert result.message == "Hola, Ada!"


def test_greet_rejects_empty_name(fake_greeter):
    with pytest.raises(EmptyNameError):
        greet(GreetingRequest(name="   "), fake_greeter)

    assert fake_greeter.delivered == []
