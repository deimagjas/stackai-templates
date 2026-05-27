# python-cli-hexagonal

Plantilla de proyecto Python para CLIs construidas con **arquitectura
hexagonal** (ports & adapters), inspirada en el ejemplo de
[ArjanCodes](https://github.com/ArjanCodes/examples/tree/main/2026/ports)
pero adaptada a una interfaz de línea de comandos con **Typer**.

Gestiona dependencias con **uv**, aplica lint y format con **ruff**
(reglas alineadas al Google Python Style Guide) y protege la
arquitectura con **tach** (equivalente Python de ArchUnit).

## Arquitectura

```
           +-----------------------------+
           |        entrypoint/          |  CLI (Typer), wiring, error map
           +--------------+--------------+
                          | depende de
           +--------------v--------------+
           |          domain/            |  modelos, puertos, use cases
           +--------------+--------------+
                          ^ implementa (estructuralmente)
           +--------------+--------------+
           |         adapters/           |  IO concreto (consola, fs, http)
           +-----------------------------+
```

**Regla de oro:** `domain/` no importa de `adapters/` ni de
`entrypoint/`. `tach check` lo verifica en cada commit y en CI.

## Estructura de directorios

```
python-cli-hexagonal/
├── README.md                      # este archivo
├── CLAUDE.md                      # reglas Google no expresables en ruff
├── pyproject.toml                 # uv + typer + ruff + pytest + tach
├── tach.toml                      # boundaries arquitectónicos
├── .pre-commit-config.yaml        # ruff + tach pre-commit
├── .github/workflows/ci.yml       # lint + format + tach + pytest
├── src/app/
│   ├── domain/                    # NÚCLEO puro, sin dependencias externas
│   │   ├── ports.py               # typing.Protocol → GreeterPort
│   │   ├── models.py              # @dataclass(frozen=True)
│   │   ├── use_cases.py           # funciones puras
│   │   └── errors.py              # DomainError jerarquía
│   ├── adapters/                  # implementaciones concretas
│   │   └── console_greeter.py
│   └── entrypoint/                # composition root + CLI Typer
│       ├── cli.py                 # typer.Typer() + mapeo DomainError
│       ├── wiring.py              # factories de puertos
│       ├── __main__.py            # python -m app.entrypoint
│       └── commands/
│           └── greet.py           # subcomando `greet`
└── tests/
    ├── conftest.py                # FakeGreeter fixture
    ├── unit/test_use_cases.py
    └── integration/test_cli.py
```

## Setup

Requiere [uv](https://docs.astral.sh/uv/) instalado.

```bash
uv sync
```

Esto crea el `.venv`, instala dependencias de runtime y de desarrollo, e
instala el paquete `app` en modo editable.

## Ejecución

Dos formas equivalentes:

```bash
uv run app greet --name Mundo
uv run python -m app.entrypoint greet --name Mundo
```

Salida esperada en verde negrita: `Hola, Mundo!`

Probar el manejo de errores de dominio:

```bash
uv run app greet --name "   "
# Error: El nombre del destinatario no puede estar vacio.
# (en rojo a stderr, exit code 1)
```

## Testing

```bash
uv run pytest
```

Coverage activo por defecto. Tests divididos en `unit/` (dominio + fake
adapter) e `integration/` (CLI end-to-end con `CliRunner`).

## Lint y format

```bash
uv run ruff check .          # detecta problemas
uv run ruff check --fix .    # corrige automáticamente
uv run ruff format .         # formatea
```

Las reglas de `ruff` están alineadas al Google Python Style Guide. Las
reglas del guide que ruff no puede expresar están en
[`CLAUDE.md`](./CLAUDE.md) y deben respetarse en code review.

## Enforcement arquitectónico

```bash
uv run tach check          # valida boundaries
uv run tach show           # imprime grafo de dependencias permitidas
uv run tach mod            # asistente para añadir nuevos módulos
```

`tach.toml` declara qué módulos pueden importar de qué módulos. Si
alguien añade `from app.adapters.x import y` dentro de
`src/app/domain/`, `tach check` falla y el commit/PR se bloquea.

### Activar pre-commit local

```bash
uv run pre-commit install
```

A partir de ahí, cada `git commit` corre ruff + tach.

## Cómo añadir un nuevo comando

1. Definir el contrato en `src/app/domain/ports.py` (nuevo `Protocol`)
   si el comando necesita un canal de IO nuevo.
2. Añadir modelos en `src/app/domain/models.py`.
3. Escribir el use case puro en `src/app/domain/use_cases.py`.
4. Implementar el adapter en `src/app/adapters/<nombre>.py`.
5. Registrar la factory del adapter en `src/app/entrypoint/wiring.py`.
6. Crear el subcomando en
   `src/app/entrypoint/commands/<nombre>.py` con una función `run(...)`.
7. Registrarlo en `src/app/entrypoint/cli.py`:
   `app.command(name="<nombre>")(<nombre>_cmd.run)`.
8. Tests: unitarios con fake adapter en `tests/unit/`; integración con
   `CliRunner` en `tests/integration/`.
9. Si el comando introduce un **paquete nuevo** bajo `src/app/`,
   añadirlo a `tach.toml` con sus `depends_on` explícitos.

## Cómo renombrar el paquete `app`

```bash
# 1. Renombrar el directorio
mv src/app src/<tu_nombre>

# 2. Sustituir el import path en todo el código
find . -type f \( -name '*.py' -o -name '*.toml' -o -name '*.yaml' \
  -o -name '*.yml' -o -name '*.md' \) \
  -not -path './.venv/*' -not -path './.git/*' \
  -exec sed -i '' 's/\bapp\b/<tu_nombre>/g' {} +

# 3. Actualizar pyproject.toml:
#    - [project] name
#    - [project.scripts] <tu_nombre> = "<tu_nombre>.entrypoint.cli:main"
#    - [tool.hatch.build.targets.wheel] packages = ["src/<tu_nombre>"]
#    - [tool.ruff.lint.per-file-ignores] paths

# 4. Re-sync
uv sync
uv run <tu_nombre> greet --name Mundo
```

## Verificación end-to-end de la plantilla

```bash
uv sync
uv run app greet --name Mundo           # → "Hola, Mundo!" verde, exit 0
uv run app greet --name "   "           # → "Error: ..."   rojo,  exit 1
uv run pytest                            # 5 tests passing
uv run ruff check .                      # All checks passed!
uv run ruff format --check .             # sin cambios pendientes
uv run tach check                        # ✓ All modules validated!
uv build                                 # genera dist/app-0.1.0-*.whl
```
