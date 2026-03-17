# Comandos de ejecucion (manual)

## Preparacion

- iniciar memoria: `engram.exe serve`
- leer contexto previo: `engram.exe context`

## Prompts por fase

- Explorer: `Usa workflows/gentleman/01_explorer.md y entrega Output contract.`
- Proposer: `Usa workflows/gentleman/02_proposer.md y entrega Plan + Validation.`
- Spec Writer: `Usa workflows/gentleman/03_spec_writer.md y entrega spec tecnica.`
- Designer: `Usa workflows/gentleman/04_designer.md y entrega decisiones de diseno.`
- Task Planner: `Usa workflows/gentleman/05_task_planner.md y arma tareas atomicas.`
- Implementer: `Usa workflows/gentleman/06_implementer.md y ejecuta por lotes pequenos.`
- Verifier: `Usa workflows/gentleman/07_verifier.md y valida criterios de aceptacion.`
- Archiver: `Usa workflows/gentleman/08_archiver.md y cierra con memoria Engram.`

## Cierre de memoria

`engram.exe save "Sesion - <tema>" "What: ... Why: ... Where: ... Learned: ..." --type discovery`
