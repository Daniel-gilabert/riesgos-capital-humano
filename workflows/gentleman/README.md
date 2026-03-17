# Gentleman Flow (Agent Teams Lite style)

Flujo multi-agente para este proyecto, inspirado en el pipeline del curso:

`Explorer -> Proposer -> (Spec Writer || Designer) -> Task Planner -> Implementer -> Verifier -> Archiver`

## Objetivo

- reducir errores por contexto largo
- dividir el trabajo por fases con contratos claros
- guardar aprendizaje en memoria persistente (Engram)

## Contrato entre fases

Cada fase debe entregar SIEMPRE:

- `What`: que hizo
- `Why`: por que esa decision
- `Where`: archivos tocados o revisados
- `Output`: resultado estructurado para la siguiente fase
- `Risks`: riesgos detectados

## Comandos rapidos

1) Levantar memoria persistente:

`engram.exe serve`

2) Guardar aprendizaje al cerrar una fase:

`engram.exe save "Fase X - resumen" "What: ... Why: ... Where: ... Learned: ..." --type discovery`

3) Consultar contexto antes de empezar una fase:

`engram.exe context`

4) Buscar decisiones historicas:

`engram.exe search "pipeline riesgos"`

## Uso recomendado

- abrir `AGENT.md` para reglas globales
- ejecutar una fase a la vez
- no saltar `Verifier`
- cerrar siempre con `Archiver` + memoria en Engram
