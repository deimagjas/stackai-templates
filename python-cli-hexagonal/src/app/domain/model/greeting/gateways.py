"""Gateways del modelo `greeting`: contratos que el dominio espera del exterior.

Usamos `typing.Protocol` (tipado estructural) para que los adapters no
necesiten heredar explicitamente. El gateway vive junto al modelo que sirve.
"""

from typing import Protocol, runtime_checkable

from app.domain.model.greeting.models import Greeting


@runtime_checkable
class GreeterPort(Protocol):
    """Canal de salida para entregar un saludo al usuario.

    `runtime_checkable` permite verificar la conformidad con `isinstance`
    (lo aprovecha el contenedor `Dependencies` de pydantic en el wiring).
    """

    def deliver(self, greeting: Greeting) -> None:
        """Entrega el saludo por el canal concreto (stdout, log, etc.)."""
        ...
