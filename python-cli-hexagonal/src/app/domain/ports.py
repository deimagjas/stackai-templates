"""Puertos: contratos que el dominio espera del exterior.

Usamos `typing.Protocol` (tipado estructural) para que los adapters no
necesiten heredar explicitamente. Esto mantiene el dominio desacoplado
de las implementaciones concretas.
"""

from typing import Protocol

from app.domain.models import Greeting


class GreeterPort(Protocol):
    """Canal de salida para entregar un saludo al usuario."""

    def deliver(self, greeting: Greeting) -> None:
        """Entrega el saludo por el canal concreto (stdout, log, etc.)."""
        ...
