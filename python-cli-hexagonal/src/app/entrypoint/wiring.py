"""Composition root: construye instancias de puertos concretas.

Centralizar el wiring aqui permite cambiar adapters (por ejemplo, swap a
un adapter de logging o de tests) modificando un unico archivo.
"""

from app.adapters.console_greeter import ConsoleGreeter
from app.domain.ports import GreeterPort


def build_greeter() -> GreeterPort:
    """Devuelve la implementacion por defecto de `GreeterPort`."""
    return ConsoleGreeter()
