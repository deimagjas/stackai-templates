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
    """Mapea `DomainError` a exit code 1 con mensaje rojo en stderr."""
    try:
        app()
    except DomainError as exc:
        typer.secho(f"Error: {exc}", fg=typer.colors.RED, err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
