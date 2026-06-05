"""Modelos de dominio inmutables del saludo."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GreetingRequest:
    """Solicitud de saludo dirigida a un destinatario.

    Attributes:
        name: Nombre del destinatario; no puede estar vacio.
    """

    name: str


@dataclass(frozen=True, slots=True)
class Greeting:
    """Resultado de una operacion de saludo.

    Attributes:
        message: Texto final a entregar al usuario.
    """

    message: str
