"""Subcomando `greet`."""

from typing import Annotated

import typer

from app.domain.model.greeting.models import GreetingRequest
from app.domain.usecase.greet.use_case import greet
from app.entrypoint.wiring import Dependencies


def run(
    ctx: typer.Context,
    name: Annotated[
        str,
        typer.Option("--name", "-n", help="Nombre del destinatario."),
    ] = "Mundo",
) -> None:
    """Saluda al destinatario indicado."""
    deps: Dependencies = ctx.obj
    greeting = greet(GreetingRequest(name=name))
    deps.greeter.deliver(greeting)
