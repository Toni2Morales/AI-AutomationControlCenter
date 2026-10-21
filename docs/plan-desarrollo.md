# Plan de desarrollo

## Estado actual
Este plan refleja el estado real del proyecto. Muchas fases están por realizar.

## Fases previstas

### Fase 0: Inspección y planificación (COMPLETADA)
- **Objetivo:** Inventariar entorno, herramientas, arquitectura y riesgos.
- **Criterios de aceptación:**
  - [x] SO, hardware y recursos identificados
  - [x] Herramientas detectadas con versiones
  - [x] Ollama accesible en localhost:11434 (sin modelos)
  - [x] Arquitectura y decisiones iniciales definidas
  - [x] Plan de trabajo aprobado

### Fase 1: Estructura inicial y documentación (EN CURSO)
- **Objetivo:** Crear estructura de carpetas, documentación en español, .env.example, .gitignore, AGENTS.md versionado, flujo Git/GitHub.
- **Criterios de aceptación:**
  - [x] Carpetas creadas (frontend, backend, database, n8n, ai-eval, postman, infra, docs)
  - [x] README.md actualizado en español, distingue planificado vs implementado
  - [x] docs/arquitectura.md en español
  - [x] docs/plan-desarrollo.md en español (este documento)
  - [x] docs/decisiones-tecnicas.md en español
  - [x] AGENTS.md creado y versionado (retirado de .gitignore)
  - [x] .env.example sin secretos
  - [x] .gitignore adecuado
  - [x] Rama de trabajo docs/project-foundation creada (sin commits en main)
  - [ ] Commits realizados y revisados
  - [ ] Rama publicada en GitHub y PR hacia main preparado (sin fusionar)

### Fase 2: Entorno backend con Python 3.12
- **Objetivo:** Preparar backend con FastAPI, entorno virtual con Python 3.12, configuración base.
- **Criterios de aceptación:**
  - [ ] Verificado Python 3.12 disponible o documentado requisito
  - [ ] Entorno virtual creado en backend/
  - [ ] Estructura base FastAPI
  - [ ] Configuración con variables de entorno
  - [ ] Sin dependencias innecesarias

### Fase 3: Infraestructura local (Docker Compose)
- **Objetivo:** Crear docker-compose.yml funcional para desarrollo local con red interna, volúmenes, health checks.
- **Criterios de aceptación:**
  - [ ] docker-compose.yml validado
  - [ ] Servicios con red interna
  - [ ] Puertos solo en 127.0.0.1 cuando expuestos
  - [ ] Volúmenes persistentes
  - [ ] Orden de arranque con health checks

### Fase 4: Base de datos and migraciones (Alembic)
- **Objetivo:** Configurar PostgreSQL, modelos base, Alembic.
- **Criterios de aceptación:**
  - [ ] Conexión DB funcional
  - [ ] Primera migración aplicada
  - [ ] Estructura base documentada

### Fase 5: Proveedor de IA (Ollama)
- **Objetivo:** Interfaz AIProvider, implementación Ollama, validation of salidas with esquemas.
- **Criterios of aceptación:**
  - [ ] Interfaz configurable
  - [ ] Conexión a http://localhost:11434
  - [ ] Validación of respuestas
  - [ ] Logs sin secretos

### Fase 6: Integración n8n and flujos
- **Objetivo:** Flujos versionados en n8n/, integración with backend.
- **Criterios of aceptación:**
  - [ ] Flujos exportados JSON
  - [ ] Integración documentada
  - [ ] Auditoría básica

### Fase 7: Frontend Angular
- **Objetivo:** Aplicación Angular en modo estricto, comunicación solo with backend.
- **Criterios of aceptación:**
  - [ ] Estructura base
  - [ ] Comunicación HTTP with backend
  - [ ] Sin acceso directo a DB/Ollama/n8n

### Fase 8: Pruebas, evaluación IA, limpieza and documentación final
- **Objetivo:** pytest, Postman, ai-eval/, Pandas, hardening, documentación completa.
- **Criterios of aceptación:**
  - [ ] Pruebas básicas pasando
  - [ ] Colección Postman
  - [ ] Casos evaluación IA
  - [ ] README and docs updated

## Notas
- No se asumen éxitos sin verificación.
- Todo desarrollo fuera of main, with PR towards main.
- Sin secretos en repo.
