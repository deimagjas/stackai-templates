"""Subcomando `greet`."""

from typing import Annotated

import typer

from app.domain.models import GreetingRequest
from app.domain.use_cases import greet
from app.entrypoint.wiring import build_greeter


def run(
    name: Annotated[
        str,
        typer.Option("--name", "-n", help="Nombre del destinatario."),
    ] = "Mundo",
) -> None:
    """Saluda al destinatario indicado."""
    greeter = build_greeter()
    request = GreetingRequest(name=name)
    greet(request, greeter)
