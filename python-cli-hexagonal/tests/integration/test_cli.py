"""Tests de integracion de la CLI con `typer.testing.CliRunner`."""

import runpy
import sys

import pytest
from typer.testing import CliRunner

from app.entrypoint.cli import app, main

runner = CliRunner()


def test_greet_default():
    result = runner.invoke(app, ["greet"])
    assert result.exit_code == 0
    assert "Hola, Mundo!" in result.stdout


def test_greet_with_name():
    result = runner.invoke(app, ["greet", "--name", "Ada"])
    assert result.exit_code == 0
    assert "Hola, Ada!" in result.stdout


def test_main_maps_domain_error_to_exit_code_1(monkeypatch, capsys):
    # `main()` es el wrapper real que traduce DomainError -> exit code 1.
    # CliRunner(app) NO atraviesa main() (el `1` lo sintetizaria Click, no
    # el sys.exit(1) del wrapper), por eso se invoca main() directamente.
    monkeypatch.setattr(sys, "argv", ["app", "greet", "--name", "   "])

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.err
    assert captured.out == ""


def test_main_maps_unexpected_error_to_generic_message(monkeypatch, capsys):
    # Una excepcion NO-DomainError debe salir con exit code 1 y un mensaje
    # generico, sin filtrar el detalle interno por stderr.
    def boom() -> None:
        internal_detail = "detalle-interno-sensible"
        raise RuntimeError(internal_detail)

    monkeypatch.setattr("app.entrypoint.cli.app", boom)

    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "inesperado" in captured.err.lower()
    assert "detalle-interno-sensible" not in captured.err


def test_dunder_main_module_maps_error_to_exit_code_1(monkeypatch, capsys):
    # Ejercita el modulo real `python -m app.entrypoint` (incluye __main__.py):
    # el mapeo DomainError -> exit code 1 debe ocurrir en el entrypoint cableado.
    monkeypatch.setattr(sys, "argv", ["app", "greet", "--name", "   "])

    with pytest.raises(SystemExit) as exc:
        runpy.run_module("app.entrypoint", run_name="__main__")

    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.err
    assert captured.out == ""
