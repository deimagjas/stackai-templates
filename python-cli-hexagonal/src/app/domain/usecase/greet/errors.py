"""Errores especificos del caso de uso `greet`."""

from app.domain.errors import DomainError


class EmptyNameError(DomainError):
    """Se intento saludar a un destinatario sin nombre."""
