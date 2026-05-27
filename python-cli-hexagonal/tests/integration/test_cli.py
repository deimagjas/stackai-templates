"""Tests de integracion de la CLI con `typer.testing.CliRunner`."""

from typer.testing import CliRunner

from app.entrypoint.cli import app

runner = CliRunner()


def test_greet_default():
    result = runner.invoke(app, ["greet"])
    assert result.exit_code == 0
    assert "Hola, Mundo!" in result.stdout


def test_greet_with_name():
    result = runner.invoke(app, ["greet", "--name", "Ada"])
    assert result.exit_code == 0
    assert "Hola, Ada!" in result.stdout
