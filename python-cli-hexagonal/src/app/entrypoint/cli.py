"""Aplicacion Typer raiz y manejo global de errores de dominio."""

import sys

import typer

from app.domain.errors import DomainError
from app.entrypoint.commands import greet as greet_cmd
from app.entrypoint.wiring import build_dependencies

app = typer.Typer(
    name="app",
    help="Plantilla CLI hexagonal.",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def _root(ctx: typer.Context) -> None:
    """Construye las dependencias una sola vez (composition root)."""
    ctx.obj = build_dependencies()


app.command(name="greet")(greet_cmd.run)


def main() -> None:
    """Mapea errores a exit code 1 con mensaje rojo en stderr.

    `DomainError` se reporta con su mensaje (es seguro mostrarlo). Cualquier
    otra excepcion es inesperada: se reporta con un mensaje generico para no
    filtrar trazas ni detalles internos por el canal de salida.
    """
    try:
        app()
    except DomainError as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
        sys.exit(1)
    except Exception:  # noqa: BLE001 - red de seguridad del entrypoint.
        typer.secho(
            "Error inesperado. Intentalo de nuevo.",
            fg=typer.colors.RED,
            err=True,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
