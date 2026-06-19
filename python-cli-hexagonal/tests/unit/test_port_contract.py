"""Contract test: ata el adapter real y el fake al puerto `GreeterPort`.

`runtime_checkable` solo comprueba que `deliver` exista, no su firma. La
conformidad estructural completa (incluida la firma) la verifica `ty`: el
adapter real via el ancla `_REAL` de aqui (y `wiring.build_dependencies`),
y el fake via el ancla en `tests/conftest.py`, junto a su definicion. Estos
tests cubren ademas el comportamiento en runtime de ambas implementaciones.
"""

from app.adapters.console_greeter import ConsoleGreeter
from app.domain.model.greeting.gateways import GreeterPort
from app.domain.model.greeting.models import Greeting

# Ancla estatica del adapter real verificada por `ty` (no en runtime).
_REAL: GreeterPort = ConsoleGreeter()


def test_real_adapter_satisfies_port_at_runtime():
    assert isinstance(ConsoleGreeter(), GreeterPort)


def test_fake_satisfies_port_at_runtime(fake_greeter):
    assert isinstance(fake_greeter, GreeterPort)


def test_real_adapter_delivers_to_stdout(capsys):
    ConsoleGreeter().deliver(Greeting(message="Hola, Ada!"))

    captured = capsys.readouterr()
    assert "Hola, Ada!" in captured.out


def test_fake_records_what_it_delivers(fake_greeter):
    fake_greeter.deliver(Greeting(message="Hola, Ada!"))

    assert fake_greeter.delivered == [Greeting(message="Hola, Ada!")]
