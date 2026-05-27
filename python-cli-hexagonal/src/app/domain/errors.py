"""Jerarquia de errores de dominio."""


class DomainError(Exception):
    """Error base del dominio. Todos los errores propios heredan de aqui."""


class EmptyNameError(DomainError):
    """Se intento saludar a un destinatario sin nombre."""
