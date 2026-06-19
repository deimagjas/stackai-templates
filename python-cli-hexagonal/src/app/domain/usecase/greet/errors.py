"""Errores especificos del caso de uso `greet`."""

from app.domain.errors import DomainError


class EmptyNameError(DomainError):
    """Se intento saludar a un destinatario sin nombre."""


class NameTooLongError(DomainError):
    """El nombre del destinatario excede el limite permitido."""


class UnsafeNameError(DomainError):
    """El nombre contiene caracteres no imprimibles (p. ej. de control)."""
