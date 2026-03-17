# AGENT.md - Guia operativa del agente

Este archivo define como debe trabajar un agente de IA en este proyecto.

## 1) Objetivo del proyecto

Aplicacion Streamlit para analisis de riesgos de capital humano con enfoque en:
- carga y limpieza de datos
- visualizacion y metricas
- analisis apoyado por servicios internos

## 2) Stack y entorno

- Lenguaje: Python 3
- UI: Streamlit
- Datos: pandas, numpy, openpyxl
- Backend opcional: Supabase

Dependencias principales en requirements.txt.

## 3) Estructura base

- app.py: entrada principal de la app
- config.py: carga de configuracion y entorno
- services/: logica de negocio y datos
- models/: modelos base
- ui/: layouts, componentes y paginas
- sample_data/: datos de ejemplo

## 4) Flujo de trabajo (Plan Mode)

Para cambios medianos o grandes, seguir este orden:

1. Entender el pedido y los archivos afectados
2. Proponer plan corto por pasos
3. Ejecutar cambios pequenos y verificables
4. Validar (lint rapido, compilacion, ejecucion local)
5. Reportar que se cambio y por que

Cuando NO usar Plan Mode estricto:
- fix pequeno en 1 archivo
- ajuste de texto o typo
- cambio trivial sin riesgo

## 5) Convenciones de codigo

- Priorizar claridad sobre ingenio
- Funciones pequenas y con una responsabilidad
- Evitar efectos colaterales ocultos
- No hardcodear secretos ni credenciales
- Mantener nombres explicitos en espanol o ingles, sin mezclar en la misma capa
- Respetar estilo existente del archivo antes de refactorizar

## 6) Reglas de seguridad y datos

- Nunca commitear .env ni llaves privadas
- Si aparece un secreto en texto plano, detener y alertar
- Para integraciones externas, usar variables de entorno desde config.py

## 7) Testing y verificacion minima

Antes de cerrar una tarea de codigo, intentar:

python -m compileall .
streamlit run app.py

Si no se puede ejecutar algo, explicar por que y dejar pasos de verificacion manual.

## 8) HITL (Human in the Loop)

Requiere aprobacion humana explicita antes de:

- borrar datos o archivos de negocio
- cambios irreversibles de esquema SQL
- operaciones con impacto productivo
- acciones con riesgo de seguridad

Para el resto, el agente puede avanzar de forma autonoma y reportar resultados.

## 9) MCP y Skills (cuando aplique)

- Usar MCP para herramientas externas (servicios, APIs, automatizaciones)
- Usar Skills para reglas internas y buenas practicas por dominio
- Cargar solo el contexto necesario para evitar ruido

## 10) Memoria operativa con Engram

Cuando haya una decision o aprendizaje importante, guardar memoria en formato:

- What: que se hizo
- Why: por que se hizo
- Where: archivos/rutas afectadas
- Learned: aprendizaje reutilizable

Objetivo: evitar amnesia entre sesiones y mejorar ejecuciones futuras.

## 11) Estilo de commits y PRs

- Commits pequenos y atomicos
- Mensajes en imperativo y enfocados en el motivo
- Incluir riesgo, impacto y validacion en la descripcion del PR

---

Regla principal: entregar cambios confiables, explicables y faciles de mantener.
