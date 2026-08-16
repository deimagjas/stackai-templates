# stackai-templates

Colección de plantillas de proyecto para StackAI.

## Plantillas disponibles

- [`python-cli-hexagonal/`](./python-cli-hexagonal) — Plantilla de
  proyecto Python para CLIs construidas con arquitectura hexagonal
  (ports & adapters). Usa **Typer**, gestiona dependencias con **uv**,
  lint y format con **ruff** (reglas alineadas al Google Python Style
  Guide) y enforcement de boundaries arquitectónicos con **tach**.

## Plantillas AI-native

Todas las plantillas de este repositorio siguen un contrato de
**harness** documentado: un conjunto explícito de guías (feedforward) y
sensores (feedback), tanto computational como inferential, en torno al
agente de código. Ese contrato está definido en
[`./AGENTS.md`](./AGENTS.md) — el documento canónico y agnóstico de
herramienta para todo el repo — y se expone a Claude Code a través de un
skill propio de cada plantilla. Los flujos de decisión de cada skill
tienen su contraparte visual en [`./docs/harness/`](./docs/harness/),
con diagramas Mermaid pensados tanto para onboarding humano como para
agentes.

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
