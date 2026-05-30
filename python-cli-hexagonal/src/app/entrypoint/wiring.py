"""Composition root: construye las dependencias concretas una sola vez.

`build_dependencies` es el unico lugar donde se eligen e instancian los
adapters. Cambiar un adapter (por ejemplo, swap a uno de logging o de
tests) se hace modificando este unico archivo.
"""

from dataclasses import dataclass

from app.adapters.console_greeter import ConsoleGreeter
from app.domain.model.greeting.gateways import GreeterPort


@dataclass(frozen=True, slots=True)
class Dependencies:
    """Contenedor de puertos concretos resueltos para la ejecucion.

    Attributes:
        greeter: Implementacion de `GreeterPort` para entregar saludos.
    """

    greeter: GreeterPort


def build_dependencies() -> Dependencies:
    """Resuelve e instancia las dependencias por defecto de la app."""
    return Dependencies(greeter=ConsoleGreeter())
