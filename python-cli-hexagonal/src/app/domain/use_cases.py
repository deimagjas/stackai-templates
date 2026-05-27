"""Use cases: funciones puras que orquestan dominio + puertos."""

from app.domain.errors import EmptyNameError
from app.domain.models import Greeting, GreetingRequest
from app.domain.ports import GreeterPort


def greet(request: GreetingRequest, greeter: GreeterPort) -> Greeting:
    """Construye y entrega un saludo.

    Args:
        request: Solicitud validada con el nombre del destinatario.
        greeter: Puerto de salida que materializa la entrega.

    Returns:
        El `Greeting` finalmente entregado (util para tests y logs).

    Raises:
        EmptyNameError: Si el nombre esta vacio o solo contiene espacios.
    """
    name = request.name.strip()
    if not name:
        msg = "El nombre del destinatario no puede estar vacio."
        raise EmptyNameError(msg)

    greeting = Greeting(message=f"Hola, {name}!")
    greeter.deliver(greeting)
    return greeting
