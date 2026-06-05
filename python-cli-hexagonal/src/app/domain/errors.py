"""Jerarquia de errores de dominio (shared kernel).

Solo vive aqui la base `DomainError`. Los errores especificos de cada
caso de uso viven junto a el (p. ej. `usecase/greet/errors.py`).
"""


class DomainError(Exception):
    """Error base del dominio. Todos los errores propios heredan de aqui."""
