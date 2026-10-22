# Plan de desarrollo

## Estado actual
Este plan refleja el estado real del proyecto tras la revisión documental. Únicamente se marcan como completados los elementos que existen y han sido verificados.

## Fases previstas

### Fase 0: Inspección y planificación (COMPLETADA)
- **Objetivo:** Inventariar entorno, herramientas, arquitectura y riesgos.
- **Criterios de aceptación:**
  - [x] Sistema operativo, hardware y recursos identificados
  - [x] Herramientas detectadas
  - [x] Ollama accesible en http://localhost:11434 (sin modelos)
  - [x] Arquitectura y decisiones iniciales definidas

### Fase 1: Estructura inicial y documentación (PARCIALMENTE COMPLETADA)
- **Objetivo:** Crear estructura de carpetas, documentación en español, plantillas seguras y flujo Git/GitHub.
- **Criterios de aceptación:**
  - [x] Estructura de carpetas creada
  - [x] README.md en español con estado real
  - [x] docs/arquitectura.md en español con componentes, comunicaciones y límites de seguridad
  - [x] docs/plan-desarrollo.md en español (este documento)
  - [x] docs/decisiones-tecnicas.md en español
  - [x] AGENTS.md versionado en español, sin referencias personales
  - [x] .env.example presente en raíz
  - [x] .gitignore configurado y AGENTS.md no ignorado
  - [x] Rama de trabajo creada (nunca en main)
  - [ ] Commits revisados y verificados
  - [ ] Rama publicada y Pull Request hacia main (sin fusionar)
- **Notas:** La existencia de archivos se verifica, pero la implementación completa aún está pendiente.

### Fase 2: Entorno backend con Python 3.12 (PENDIENTE)
- **Objetivo:** Preparar backend con FastAPI, entorno virtual con Python 3.12, configuración base.
- **Criterios de aceptación:**
  - [ ] Python 3.12 verificado o requisito documentado
  - [ ] Entorno virtual creado en ackend/
  - [ ] Estructura base FastAPI
  - [ ] Configuración con variables de entorno
  - [ ] Sin dependencias innecesarias

### Fase 3: Infraestructura local (PENDIENTE)
- **Objetivo:** Orquestación local con Docker Compose (cuando proceda), red interna, volúmenes y health checks.
- **Criterios de aceptación:**
  - [ ] docker-compose.yml validado (solo si creado)
  - [ ] Red interna configurada
  - [ ] Puertos limitados a 127.0.0.1 cuando se expongan
  - [ ] Volúmenes persistentes
  - [ ] Orden de arranque con health checks

### Fase 4: Base de datos y migraciones (PENDIENTE)
- **Objetivo:** PostgreSQL, modelos base, Alembic.
- **Criterios de aceptación:**
  - [ ] Conexión a PostgreSQL funcional
  - [ ] Primera migración creada y aplicada
  - [ ] Esquema base documentado

### Fase 5: Proveedor de IA (Ollama) (PENDIENTE)
- **Objetivo:** Interfaz AIProvider configurable, implementación OllamaProvider, validación de salidas con esquemas explícitos.
- **Criterios de aceptación:**
  - [ ] Interfaz definida y desacoplada
  - [ ] Conexión a http://localhost:11434
  - [ ] Validación de respuestas contra esquema
  - [ ] Logs sin secretos

### Fase 6: Integración n8n y flujos (PENDIENTE)
- **Objetivo:** Flujos versionados en
8n/, integración con backend, auditoría.
- **Criterios de aceptación:**
  - [ ] Flujos exportados en formato JSON
  - [ ] Integración documentada
  - [ ] Registro de auditoría básico

### Fase 7: Frontend Angular (PENDIENTE)
- **Objetivo:** Aplicación Angular en modo estricto, comunicación únicamente con FastAPI.
- **Criterios de aceptación:**
  - [ ] Estructura base creada
  - [ ] Comunicación HTTP con backend
  - [ ] Sin acceso directo to PostgreSQL, Ollama o n8n

### Fase 8: Pruebas, evaluación, limpieza y documentación final (PENDIENTE)
- **Objetivo:** pytest, Postman, i-eval/, Pandas, hardening, documentación actualizada.
- **Criterios de aceptación:**
  - [ ] Pruebas básicas ejecutadas and verificadas
  - [ ] Colección Postman actualizada
  - [ ] Casos de evaluación de IA definidos
  - [ ] Documentación reflejando estado real

## Notas
- No se marcarán tareas como completadas sin existencia de archivos o comprobaciones reales.
- Desarrollo fuera of main. Pull Request hacia main, sin fusionar automáticamente.
- Sin secretos en el repositorio.
- No se crea docker-compose.yml ni código de aplicación en esta fase.
