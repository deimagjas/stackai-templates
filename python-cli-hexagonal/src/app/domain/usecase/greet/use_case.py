"""Caso de uso `greet`: funcion pura que construye un saludo."""

from app.domain.model.greeting.models import Greeting, GreetingRequest
from app.domain.usecase.greet.errors import EmptyNameError


def greet(request: GreetingRequest) -> Greeting:
    """Construye un saludo a partir de la solicitud.

    Funcion pura: no produce efectos de salida. La entrega del saludo es
    responsabilidad del entrypoint, que invoca el `GreeterPort`.

    Args:
        request: Solicitud con el nombre del destinatario.

    Returns:
        El `Greeting` construido.

    Raises:
        EmptyNameError: Si el nombre esta vacio o solo contiene espacios.
    """
    name = request.name.strip()
    if not name:
        msg = "El nombre del destinatario no puede estar vacio."
        raise EmptyNameError(msg)

    return Greeting(message=f"Hola, {name}!")
