"""Adapter de `GreeterPort` que escribe a la consola via Typer."""

from dataclasses import dataclass

import typer

from app.domain.model.greeting.models import Greeting


@dataclass(frozen=True, slots=True)
class ConsoleGreeter:
    """Entrega saludos a stdout coloreados con Typer.

    Cumple estructuralmente con `app.domain.model.greeting.gateways.GreeterPort`.

    Attributes:
        color: Color de Typer aplicado al texto del saludo.
    """

    color: str = typer.colors.GREEN

    def deliver(self, greeting: Greeting) -> None:
        """Escribe el saludo en stdout con color."""
        typer.secho(greeting.message, fg=self.color, bold=True)
