# Reglas de estilo y arquitectura (complemento a ruff y tach)

Este documento recoge las reglas del
[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
que `ruff` **no** puede imponer automáticamente, además de las
invariantes arquitectónicas específicas de esta plantilla.

Lo que sí se automatiza está en `pyproject.toml` (ruff) y en `tach.toml`
(boundaries). Lo que sigue debe respetarse manualmente y revisarse en
code review.

## 0. Desviaciones conscientes respecto a Google

- **Line length: 88** (Google = 80). Adoptamos el default de Black/ruff
  por alineamiento con el ecosistema moderno.
- **Indent: 4 espacios** (Google permite 2 o 4). PEP 8 y default de
  toda la herramienta Python.

## 1. Arquitectura hexagonal (invariantes duras)

Estas reglas las **fuerza `tach check`**. No deben relajarse:

- `app.domain` **nunca** importa de `app.adapters` ni `app.entrypoint`.
- `app.adapters` no importa de `app.entrypoint`.
- No se permiten dependencias circulares entre módulos.
- Cualquier paquete nuevo bajo `src/app/` debe declararse en
  `tach.toml` con sus `depends_on` explícitos.

Reglas adicionales no automatizadas:

- Las dependencias externas (typer, requests, sqlalchemy, etc.) viven
  solo en `adapters/` o `entrypoint/`, **nunca** en `domain/`.
- Los fakes/mocks de test viven en `tests/conftest.py` o en archivos
  bajo `tests/`, **nunca** en `src/`.
- El mapeo de excepciones de dominio al canal de salida (códigos de
  salida, colores, formatos) vive **solo** en `entrypoint/cli.py`. El
  dominio no conoce `typer.Exit`.

## 2. Power features prohibidas (Google §2.19)

- No usar metaclases salvo justificación arquitectónica explícita.
- No usar reflexión dinámica (`getattr`/`setattr` con strings derivados
  de input externo) sin comentario que la justifique.
- No monkey-patchear módulos de terceros.
- No usar import hooks ni manipular `sys.modules`.

## 3. Threading y concurrencia (Google §2.17)

- No introducir `threading`/`multiprocessing` sin justificación
  documentada en el PR.
- Preferir `concurrent.futures` o `asyncio` sobre `threading.Thread`
  pelado.
- Estructuras compartidas: usar `queue.Queue` o equivalentes
  thread-safe.

## 4. Docstrings (Google §3.8)

`ruff` con `convention = "google"` cubre formato y secciones, pero estas
reglas son cualitativas:

- Módulos: docstring de una línea como mínimo.
- Clases públicas: docstring con sección `Attributes:` cuando aplique.
- Funciones públicas: secciones `Args:`, `Returns:`, `Raises:` cuando
  apliquen.
- Funciones privadas (`_foo`): pueden omitir secciones pero conservan
  un resumen.
- **No** documentar tipos en docstring si ya están en la anotación.

## 5. Comentarios (Google §3.8.5)

- TODOs siempre con autor: `# TODO(usuario): descripción de qué falta`.
- Comentarios en frases completas, con mayúscula inicial y punto final.
- Esta plantilla usa **español** por preferencia del autor; mantener
  consistencia dentro del proyecto.

## 6. Excepciones (Google §2.4)

- Toda excepción propia hereda de `app.domain.errors.DomainError`.
- `except:` desnudo está prohibido (`ruff BLE001` lo bloquea, pero
  también aplica a `except Exception:` sin justificación).
- No usar excepciones para flujo de control normal.
- El mapeo `DomainError → typer.Exit` vive **solo** en
  `entrypoint/cli.py`.

## 7. Mutable global state (Google §2.5)

- Prohibido. Toda dependencia llega por inyección (puertos + wiring).
- Constantes en `UPPER_CASE` son aceptables si son inmutables.

## 8. Nested classes / inner functions (Google §2.16)

- Evitar clases anidadas salvo factory patterns claros.
- Closures solo cuando capturan estado relevante; si no, sacar a
  top-level.

## 9. Properties (Google §2.15)

- `@property` solo para acceso O(1) sin side effects observables.
- Si la propiedad puede fallar o es costosa, usar un método `get_*()`
  explícito.

## 10. Default mutable arguments (Google §2.12)

- `ruff B006` lo bloquea, pero recordatorio: usar `None` como sentinela
  y construir el default dentro del cuerpo.

## 11. Lambdas (Google §2.10)

- Solo para callbacks de una línea pasados a `sorted`, `map`, etc.
- Nunca asignar una lambda a un nombre (usar `def`). Lo cubre `E731`.

## 12. Conditional expressions (Google §2.11)

- Una sola expresión ternaria por línea. Anidadas → usar `if`/`else`.

## 13. Imports (Google §2.13)

- Siempre absolutos (`ruff TID252` configurado).
- Orden: stdlib, third-party, local (lo gestiona `I`).
- Un import por línea.

## 14. Type annotations (Google §2.21)

- Obligatorias en toda función pública y atributos públicos de clases
  (`ruff ANN`).
- `Any` solo en interfaces dinámicas justificadas (`ANN401` en
  `ignore`).
- Preferir `typing.Protocol` sobre ABCs para puertos.

## 15. Funciones largas (Google §3.18)

- Si una función excede ~40 líneas, considerar partirla. `ruff
  PLR0915` da una señal pero no cubre todos los casos; revisar en code
  review.

## 16. Logging (Google §2.18)

- `print()` está prohibido en código de producción (`ruff T201`).
- Toda salida al usuario pasa por un adapter (p. ej. `ConsoleGreeter`).
- Para logs internos: `logging.getLogger(__name__)` con lazy
  formatting: `logger.info("user %s", user_id)`. f-strings dentro de
  log calls los bloquea `ruff G004`.

## 17. Naming (Google §3.16)

`ruff N` cubre la mayoría. Convenciones:

- `module_name`, `package_name`
- `ClassName`, `ExceptionName`
- `function_name`, `method_name`
- `GLOBAL_CONSTANT_NAME`
- `global_var_name`, `instance_var_name`, `function_parameter_name`,
  `local_var_name`
- "Interno": prefijo `_`. Módulos internos: prefijo `_` en el nombre
  del archivo.

## 18. Política de evolución de la arquitectura

Cuando se añada un nuevo caso de uso o adapter:

1. Seguir los pasos de "Cómo añadir un nuevo comando" del README.
2. Si se introduce un paquete nuevo bajo `src/app/`, registrarlo en
   `tach.toml` con sus `depends_on` explícitos. Sin esto, `tach check`
   falla.
3. **Nunca** añadir `app.adapters` o `app.entrypoint` a `depends_on`
   de `app.domain`. Esa es la invariante que protege la arquitectura.
