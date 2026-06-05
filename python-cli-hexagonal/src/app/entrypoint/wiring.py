"""Composition root: construye las dependencias concretas una sola vez.

`build_dependencies` es el unico lugar donde se eligen e instancian los
adapters. Cambiar un adapter (por ejemplo, swap a uno de logging o de
tests) se hace modificando este unico archivo.
"""

from pydantic import BaseModel, ConfigDict

from app.adapters.console_greeter import ConsoleGreeter
from app.domain.model.greeting.gateways import GreeterPort


class Dependencies(BaseModel):
    """Contenedor de puertos concretos resueltos para la ejecucion.

    Es un modelo pydantic inmutable: valida en construccion que cada
    puerto inyectado cumpla su `Protocol` (via `runtime_checkable`).

    Attributes:
        greeter: Implementacion de `GreeterPort` para entregar saludos.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True, frozen=True)

    greeter: GreeterPort


def build_dependencies() -> Dependencies:
    """Resuelve e instancia las dependencias por defecto de la app."""
    return Dependencies(greeter=ConsoleGreeter())
