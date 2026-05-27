# stackai-templates

Colección de plantillas de proyecto para StackAI.

## Plantillas disponibles

- [`python-cli-hexagonal/`](./python-cli-hexagonal) — Plantilla de
  proyecto Python para CLIs construidas con arquitectura hexagonal
  (ports & adapters). Usa **Typer**, gestiona dependencias con **uv**,
  lint y format con **ruff** (reglas alineadas al Google Python Style
  Guide) y enforcement de boundaries arquitectónicos con **tach**.

## Uso

Copia el directorio de la plantilla que necesites y sigue su README:

```bash
cp -R python-cli-hexagonal/ ../mi-nuevo-proyecto
cd ../mi-nuevo-proyecto
uv sync
uv run app greet --name Mundo
```

El README de cada plantilla documenta cómo renombrar el paquete y
cómo añadir nuevos casos de uso preservando la arquitectura.
