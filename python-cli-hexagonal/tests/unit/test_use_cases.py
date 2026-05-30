"""Tests unitarios del caso de uso puro `greet`."""

import pytest

from app.domain.model.greeting.models import Greeting, GreetingRequest
from app.domain.usecase.greet.errors import EmptyNameError
from app.domain.usecase.greet.use_case import greet


def test_greet_builds_message():
    result = greet(GreetingRequest(name="Ada"))

    assert result == Greeting(message="Hola, Ada!")


def test_greet_trims_whitespace():
    result = greet(GreetingRequest(name="  Ada  "))

    assert result.message == "Hola, Ada!"


def test_greet_rejects_empty_name():
    with pytest.raises(EmptyNameError):
        greet(GreetingRequest(name="   "))
