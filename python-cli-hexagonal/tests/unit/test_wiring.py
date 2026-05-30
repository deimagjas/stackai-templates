"""Tests del composition root `Dependencies` (modelo pydantic)."""

import pytest
from pydantic import ValidationError

from app.entrypoint.wiring import Dependencies, build_dependencies


def test_build_dependencies_returns_valid_container():
    deps = build_dependencies()

    assert hasattr(deps.greeter, "deliver")


def test_dependencies_rejects_non_conforming_greeter():
    with pytest.raises(ValidationError):
        # Tipo invalido a proposito: validamos el rechazo en runtime.
        Dependencies(greeter=object())  # ty: ignore[invalid-argument-type]


def test_dependencies_is_frozen(fake_greeter):
    deps = Dependencies(greeter=fake_greeter)

    with pytest.raises(ValidationError):
        deps.greeter = fake_greeter
