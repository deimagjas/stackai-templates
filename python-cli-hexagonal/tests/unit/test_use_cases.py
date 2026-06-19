"""Tests unitarios del caso de uso puro `greet`."""

import pytest

from app.domain.model.greeting.models import Greeting, GreetingRequest
from app.domain.usecase.greet.errors import (
    EmptyNameError,
    NameTooLongError,
    UnsafeNameError,
)
from app.domain.usecase.greet.use_case import MAX_NAME_LENGTH, greet


def test_greet_builds_message():
    result = greet(GreetingRequest(name="Ada"))

    assert result == Greeting(message="Hola, Ada!")


def test_greet_trims_whitespace():
    result = greet(GreetingRequest(name="  Ada  "))

    assert result.message == "Hola, Ada!"


def test_greet_rejects_empty_name():
    with pytest.raises(EmptyNameError):
        greet(GreetingRequest(name="   "))


def test_greet_accepts_name_at_max_length():
    name = "A" * MAX_NAME_LENGTH

    assert greet(GreetingRequest(name=name)).message == f"Hola, {name}!"


def test_greet_rejects_too_long_name():
    with pytest.raises(NameTooLongError):
        greet(GreetingRequest(name="A" * (MAX_NAME_LENGTH + 1)))


def test_greet_rejects_control_characters():
    with pytest.raises(UnsafeNameError):
        greet(GreetingRequest(name="Ada\x07"))
