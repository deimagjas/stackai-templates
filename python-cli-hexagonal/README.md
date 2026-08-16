# python-cli-hexagonal

Plantilla de proyecto Python para CLIs construidas con **arquitectura
hexagonal** (ports & adapters), inspirada en el ejemplo de
[ArjanCodes](https://github.com/ArjanCodes/examples/tree/main/2026/ports)
pero adaptada a una interfaz de línea de comandos con **Typer**.

Gestiona dependencias con **uv**, aplica lint y format con **ruff**
(reglas alineadas al Google Python Style Guide), verifica tipos y la
conformidad estructural de los puertos con **ty**, y protege la
arquitectura con **tach** (equivalente Python de ArchUnit).

## Arquitectura

El dominio se organiza en dos capas al estilo del scaffold de
[Bancolombia](https://bancolombia.github.io/scaffold-clean-architecture/):
una capa `model/` donde cada modelo vive en su propio paquete junto a su
*gateway* (puerto), y una capa `usecase/` separada que depende de los
modelos.

```
           +-----------------------------------+
           |            entrypoint/            |  CLI (Typer), composition
           |                                  |  root, mapeo de errores
           +----------------+-----------------+
                            | depende de
           +----------------v-----------------+
           |       domain/usecase/           |  funciones puras; retornan
           |                                  |  resultados de dominio
           +----------------+-----------------+
                            | depende de
           +----------------v-----------------+
           |        domain/model/            |  entidades + gateways
           |                                  |  (puertos) por feature
           +----------------+-----------------+
                            ^ implementa (estructuralmente)
           +----------------+-----------------+
           |            adapters/             |  IO concreto (consola, fs)
           +-----------------------------------+
```

**Reglas de oro** (verificadas por `tach check` en cada commit y en CI):

- `domain/model/` no importa de ninguna otra capa.
- `domain/usecase/` depende solo de `domain/model/` (y del kernel
  compartido `domain/errors.py`), nunca al reves.
- `domain/` nunca importa de `adapters/` ni de `entrypoint/`.

Los **use cases son puros**: construyen y retornan un resultado de
dominio; la entrega por un puerto (p. ej. escribir a consola) ocurre en
el `entrypoint/`, no en el dominio.

## Estructura de directorios

```
python-cli-hexagonal/
├── README.md                      # este archivo
├── AGENTS.md                      # reglas Google no expresables en ruff
│                                   # + harness inventory
├── CLAUDE.md                      # importa AGENTS.md via @AGENTS.md
├── pyproject.toml                 # uv + typer + ruff + pytest + tach
├── tach.toml                      # boundaries arquitectónicos
├── .pre-commit-config.yaml        # ruff + tach pre-commit
├── .claude/skills/
│   ├── tdd-harness/SKILL.md       # skill de desarrollo guiado por tests
│   └── adversarial-review/SKILL.md # skill de revisión adversarial
├── .github/workflows/
│   ├── ci.yml                     # lint + format + tach + pytest
│   └── mutation-testing.yml       # mutmut en CI
├── src/app/
│   ├── domain/                    # NÚCLEO puro, sin dependencias externas
│   │   ├── errors.py              # DomainError base (shared kernel)
│   │   ├── model/                 # capa de modelos: entidad + gateway
│   │   │   └── greeting/
│   │   │       ├── models.py      # @dataclass(frozen=True)
│   │   │       └── gateways.py    # typing.Protocol → GreeterPort
│   │   └── usecase/               # capa de casos de uso (puros)
│   │       └── greet/
│   │           ├── use_case.py    # greet(request) -> Greeting
│   │           └── errors.py      # EmptyNameError(DomainError)
│   ├── adapters/                  # implementaciones concretas
│   │   └── console_greeter.py
│   └── entrypoint/                # composition root + CLI Typer
│       ├── cli.py                 # typer.Typer() + mapeo DomainError
│       ├── wiring.py              # Dependencies + build_dependencies()
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

Coverage activo por defecto. Tests divididos en `unit/` (use case puro y
entrega vía fake adapter) e `integration/` (CLI end-to-end con
`CliRunner`).

## Lint y format

```bash
uv run ruff check .          # detecta problemas
uv run ruff check --fix .    # corrige automáticamente
uv run ruff format .         # formatea
```

Las reglas de `ruff` están alineadas al Google Python Style Guide. Las
reglas del guide que ruff no puede expresar están en
[`AGENTS.md`](./AGENTS.md) (que `CLAUDE.md` importa vía `@AGENTS.md`) y
deben respetarse en code review.

## Type checking

```bash
uv run ty check              # verifica tipos y conformidad de puertos
```

`ty` (de Astral, mismo ecosistema que `uv` y `ruff`) comprueba que cada
adapter satisface estructuralmente el `Protocol` de su gateway. Sin esto,
un cambio en la firma de un puerto pasaría lint y tests y solo fallaría
en runtime. La conformidad se ancla en `wiring.py`, donde el adapter se
devuelve tipado como el puerto.

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

## Harness AI-native

Esta plantilla incluye un **harness** pensado para que agentes de IA
(y humanos) desarrollen con retroalimentación continua sobre la calidad
del código, no solo sobre su corrección superficial. Las reglas y el
inventario del harness viven en [`./AGENTS.md`](./AGENTS.md); las dos
skills que lo operan están en
[`.claude/skills/tdd-harness/SKILL.md`](./.claude/skills/tdd-harness/SKILL.md)
y
[`.claude/skills/adversarial-review/SKILL.md`](./.claude/skills/adversarial-review/SKILL.md);
el diseño y la justificación del harness a nivel de repo están en
[`../docs/harness/`](../docs/harness/).

El harness combina dos tipos de señal: un **sensor computacional**
(métricas deterministas como CRAP y mutation score, que dan
**feedback** rápido y objetivo sobre qué código está mal probado) y un
**sensor inferencial** (revisión adversarial por agente, que da
**feedforward** sobre riesgos de diseño antes de que se conviertan en
bugs). Ambos se ejecutan localmente y en CI para que ningún cambio
dependa solo del juicio del autor.

Comandos nuevos:

```bash
uv run crap-sensor --source-dir src/app --coverage-json coverage.json
# → métrica CRAP (Change Risk Anti-Patterns) por función/módulo
uv run mutmut run
# → mutation testing: mata mutantes para validar que los tests
#   realmente detectan regresiones, no solo que pasan
```

> **Nota sobre `crap-sensor`:** la dependencia declarada en
> `pyproject.toml` apunta hoy a una **ruta local** (`../../crap-sensor`),
> asumiendo que `crap-sensor` está clonado como hermano de
> `stackai-templates` en `/Users/deimagjas/qubits.cloud/` en esta
> máquina. Quien clone esta plantilla en otro entorno debe **o bien**
> clonar `crap-sensor` también como directorio hermano en esa misma
> ruta relativa, **o bien** reemplazar esa dependencia por una
> referencia a PyPI o `git+https://...` una vez que el paquete esté
> publicado. Tras cualquier cambio en `crap-sensor`, correr
> `uv sync --reinstall-package crap-sensor` para que la plantilla recoja
> el código actualizado (una dependencia de ruta local no se re-detecta
> automáticamente con un `uv sync` normal).

> **Nota sobre `mutmut` en macOS:** `mutmut` 3.x lanza cada mutante con
> `os.fork()` directo (no `multiprocessing`). En esta plantilla, corrido
> localmente en macOS (Python 3.13), **todos** los mutantes terminan como
> `timeout` de forma uniforme, independientemente de su complejidad —
> incluso probando con `OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES` (el
> workaround estándar para crashes de `fork()` en macOS). El patrón
> (timeout uniforme, no relacionado a la complejidad del mutante) apunta
> a un deadlock en el hijo forkeado, no a tests genuinamente lentos — un
> problema conocido de mezclar `os.fork()` con frameworks que usan hilos
> en background (pytest/coverage), no algo corregible desde la
> configuración de este proyecto. El workflow `mutation-testing.yml`
> corre en `ubuntu-latest`, donde `fork()` no tiene esta fragilidad
> específica de macOS — se espera que funcione en CI aunque no funcione
> en desarrollo local en Mac; esto no se ha podido verificar aún sin
> disparar el workflow en GitHub Actions.

## Cómo añadir un nuevo comando

1. Crear el paquete de modelo en
   `src/app/domain/model/<feature>/`:
   - `models.py` con los `@dataclass(frozen=True)` de la feature.
   - `gateways.py` con el `Protocol` del puerto, **junto al modelo**,
     si el comando necesita un canal de IO nuevo.
2. Crear el paquete de caso de uso en
   `src/app/domain/usecase/<feature>/`:
   - `use_case.py` con una **función pura** que reciba la solicitud y
     **retorne** un resultado de dominio (no entrega IO).
   - `errors.py` con los errores específicos de la feature, que heredan
     de `app.domain.errors.DomainError`.
3. Implementar el adapter en `src/app/adapters/<nombre>.py` que cumpla
   estructuralmente el `Protocol` del gateway.
4. Añadir el puerto como campo de `Dependencies` y construirlo en
   `build_dependencies()` dentro de `src/app/entrypoint/wiring.py`
   (composition root único).
5. Crear el subcomando en
   `src/app/entrypoint/commands/<nombre>.py` con una función
   `run(ctx: typer.Context, ...)` que: lea `ctx.obj` (las
   `Dependencies`), invoque el use case puro y luego entregue el
   resultado por el puerto.
6. Registrarlo en `src/app/entrypoint/cli.py`:
   `app.command(name="<nombre>")(<nombre>_cmd.run)`.
7. Tests: unitarios del use case puro (afirman sobre el valor retornado)
   y del puerto con un fake en `tests/unit/`; integración con
   `CliRunner` en `tests/integration/`.
8. **No** suele hacer falta tocar `tach.toml`: las features nuevas viven
   dentro de las capas ya declaradas (`app.domain.model`,
   `app.domain.usecase`). Solo se añade a `tach.toml` si introduces una
   **capa nueva** de primer nivel bajo `src/app/`.

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
uv run pytest                            # 6 tests passing
uv run ruff check .                      # All checks passed!
uv run ruff format --check .             # sin cambios pendientes
uv run ty check                          # All checks passed!
uv run tach check                        # ✓ All modules validated!
uv run crap-sensor --source-dir src/app --coverage-json coverage.json
                                          # → reporte CRAP por función
uv run mutmut run                        # → mutation score
uv build                                 # genera dist/app-0.1.0-*.whl
```
