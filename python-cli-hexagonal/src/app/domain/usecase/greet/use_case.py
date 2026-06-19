"""Caso de uso `greet`: funcion pura que construye un saludo."""

from app.domain.model.greeting.models import Greeting, GreetingRequest
from app.domain.usecase.greet.errors import (
    EmptyNameError,
    NameTooLongError,
    UnsafeNameError,
)

MAX_NAME_LENGTH = 100
"""Longitud maxima admitida para el nombre del destinatario."""


def greet(request: GreetingRequest) -> Greeting:
    """Construye un saludo a partir de la solicitud.

    Funcion pura: no produce efectos de salida. La entrega del saludo es
    responsabilidad del entrypoint, que invoca el `GreeterPort`. Valida el
    nombre como regla de dominio antes de embeberlo en el mensaje.

    Args:
        request: Solicitud con el nombre del destinatario.

    Returns:
        El `Greeting` construido.

    Raises:
        EmptyNameError: Si el nombre esta vacio o solo contiene espacios.
        NameTooLongError: Si el nombre excede `MAX_NAME_LENGTH` caracteres.
        UnsafeNameError: Si el nombre contiene caracteres no imprimibles.
    """
    name = request.name.strip()
    if not name:
        msg = "El nombre del destinatario no puede estar vacio."
        raise EmptyNameError(msg)
    if len(name) > MAX_NAME_LENGTH:
        msg = f"El nombre no puede superar {MAX_NAME_LENGTH} caracteres."
        raise NameTooLongError(msg)
    if not name.isprintable():
        msg = "El nombre contiene caracteres no permitidos."
        raise UnsafeNameError(msg)

    return Greeting(message=f"Hola, {name}!")
