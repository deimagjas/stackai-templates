---
name: dynamicsdlc
description: >-
  Ciclo SDLC dinámico plan→código→revisión adversarial con tres agentes Orca,
  cada uno en su propio worktree y rama, traspasando solo por commits. Úsalo
  cuando el usuario pida construir una feature con planificador, codificador y
  revisor adversarial, o invoque /dynamicsdlc <feature>. Aplica a cualquier
  aplicación o lenguaje.
---

# dynamicsdlc

Eres el **planificador y coordinador**. Carga primero `orchestration`
(`orca skills get orchestration`) y úsalo como coordinador supervisado. No sustituyas
Orca por subagentes de la herramienta Agent. Nunca hagas push ni merge a la rama principal.

## Entradas (pregunta solo lo que falte y no se pueda deducir del repo)

- `<slug>`: nombre corto de la feature.
- `<app_dir>`: carpeta de la aplicación (raíz del repo si no hay monorepo).
- Objetivo, alcance y fuera de alcance.
- `<checks>`: comandos de verificación del proyecto. Descúbrelos (README, CLAUDE.md,
  Makefile, pyproject/package.json, CI) y ponlos en el plan: tests, lint, formato,
  tipos, límites de arquitectura y un smoke test ejecutable de la feature.
- Reglas del proyecto: lee CLAUDE.md/AGENTS.md y el archivo de límites de capas, si existen.

## Roles

| Rol | Agente | Hace |
|---|---|---|
| Planificador | esta sesión | Escribe y commitea el plan; coordina; no toca código de la feature |
| Codificador | `--agent claude` (modelo por defecto) | Lee el plan del commit, implementa, commitea |
| Adversarial | `--agent claude --model <modelo_fuerte> --effort high` | Solo revisa; commitea su informe, nunca código |

El **único canal de traspaso son los commits**. Los workers reciben rama y SHA, no rutas
de otro worktree. Un solo worker edita a la vez; las rondas son secuenciales.

## Convenciones

- Ramas: `agent/<slug>/plan`, `agent/<slug>/rN-code`, `agent/<slug>/rN-review`.
- Artefactos en `.agents/plans/<slug>/`: `plan.md` (planificador), `review-rN.md` (adversarial).
- Prefijos de commit: `plan:`, `feat:`, `review:`. Cada rol commitea solo lo suyo.
- Máximo **3 rondas**.

## Flujo

0. **Preparación**: `orca status --json`, `git status` limpio, crear `agent/<slug>/plan`,
   `orca orchestration run-create --objective "<slug>: ciclo plan/code/review" --json`.
1. **Plan** (`plan.md`): contexto, alcance, fuera de alcance, archivos a crear/modificar,
   invariantes, criterios de aceptación verificables (los `<checks>` + smoke test) y casos
   borde. Commit `plan:` y anota el SHA.
2. **Codificador** (ronda N): `worker-start --worktree new-child --base-branch <base>
   --name <slug>-rN-code --agent claude --spec ... --json`. La base es la rama del plan en
   la ronda 1 y `rN-1-review` en las siguientes. La spec incluye: rama base y SHA; leer
   `plan.md` y el último `review-r*.md`; cambio, restricciones y carpeta editable; crear
   `agent/<slug>/rN-code` y commitear `feat:` sin push; criterios de aceptación; cierre con
   `worker_done` + SHA + rama.
3. **Adversarial** (ronda N): comprueba `git cat-file -t <sha>` y lanza con `--base-branch
   agent/<slug>/rN-code --model <modelo_fuerte> --effort high`. Verifica en el recibo que
   `launch.effective.model` sea el pedido. La spec: solo revisar
   (`git diff <sha_plan>..<sha_codigo>`), ejecutar los `<checks>`, probar casos borde y
   regresiones, y escribir `review-rN.md` con hallazgos numerados (archivo:línea, severidad,
   arreglo) o `APROBADO`; commit `review:` en `agent/<slug>/rN-review`. Cierre
   `--outcome succeeded` sin hallazgos accionables o `--outcome failed` con ellos. Sin
   trivialidades de estilo ni duplicación fuera de alcance.
4. **Decisión**: `check --wait --types worker_done,escalation,question`. Valida que el
   dispatch sea el esperado y lee el resultado **desde el commit**
   (`git show <sha> --stat`, `git show <sha>:.agents/plans/<slug>/review-rN.md`).
   `succeeded` → fin. `failed` y N<3 → ronda N+1 desde `rN-review`. N=3 con hallazgos →
   detente y reporta. Tras cada settlement: `worker-release` (o `worker-retain`) y confirma
   el ack con el siguiente `check --ack <delivery_id>`. No termines hasta que
   `worker-list --run <run_id> --terminal-state reclaimable` salga vacío.

## Reglas de redacción del plan (lecciones aprendidas)

- **Invariante sobre tests existentes**: escribe «los tests de *comportamiento* de lo
  existente no cambian; los tests de contenedores compartidos (p. ej. composition root) se
  extienden con el nuevo campo». Un cambio inevitable en un contenedor compartido no debe
  contradecir el plan.
- Lista explícitamente los **archivos compartidos** que se pueden modificar de forma
  aditiva (registro de comandos, wiring, fixtures).
- Los casos borde del plan deben aparecer en **ambos niveles** (unit e integración) o decir
  en cuál basta.
- Indica el nombre real de los módulos existentes (el nombre de la feature puede no coincidir
  con el de la carpeta, p. ej. `greet` vs `greeting`) para que el codificador replique el patrón.
- Si quieres ejercitar el bucle con hallazgos, añade un requisito más exigente; una feature
  trivial se aprueba en la ronda 1.

## Reglas de seguridad

- Si un worker queda en un diálogo (p. ej. Bypass Permissions) o hay timeout: no lo aceptes
  ni reintentes a ciegas; inspecciona con `worker-list`/`worker-read` y pide al usuario que lo
  acepte; luego reintenta con `--retry-of`.
- Si `--worktree new-child` o `--base-branch` fallan, repórtalo con el error exacto; no
  improvises otra topología.
- Ausencia de señal no autoriza stop/abandon/retry/release; solo prueba positiva de salida.

## Reporte final

Por ronda: rama, SHA, dispatch, outcome y hallazgos clave. Modelo efectivo del adversarial.
Ramas y worktrees creados, estado de verificación (los `<checks>`), y confirmación de que no
hubo push ni merge.
