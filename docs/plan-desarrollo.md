# Plan de desarrollo

## Estado actual

Este plan refleja el estado real del proyecto. Únicamente se marcan como completados los elementos que existen y han sido verificados. La imagen del backend está construida, los cuatro servicios están arrancados y saludables, la conectividad interna está verificada y la migración `b7c1e4f2a9d3` está aplicada.

## Fases

### Fase 0: Inspección y planificación (COMPLETADA)

- **Objetivo:** inventariar entorno, herramientas, arquitectura y riesgos.
- **Criterios de aceptación:**
  - [x] Sistema operativo, hardware y recursos identificados.
  - [x] Herramientas detectadas.
  - [x] Arquitectura y decisiones iniciales definidas.
  - [x] Estrategia de ejecución local revisada: Angular en Windows; FastAPI, PostgreSQL, n8n y Ollama en Docker.

### Fase 1: Estructura inicial y documentación (PARCIALMENTE COMPLETADA)

- **Objetivo:** crear estructura de carpetas, documentación en español, plantillas seguras y flujo Git/GitHub.
- **Criterios de aceptación:**
  - [x] Estructura de carpetas creada.
  - [x] README.md en español con estado real.
  - [x] `docs/arquitectura.md` en español con componentes, comunicaciones y límites de seguridad.
  - [x] `docs/plan-desarrollo.md` en español.
  - [x] `docs/decisiones-tecnicas.md` en español.
  - [x] `AGENTS.md` versionado en español.
  - [x] `.env.example` presente en la raíz.
  - [x] `.gitignore` configurado.
  - [x] Ramas de trabajo y Pull Requests documentados.
  - [ ] Commits revisados y verificados.
  - [ ] Rama publicada y Pull Request hacia `main` (sin fusionar).
- **Notas:** la estructura y la documentación existen; quedan pendientes la revisión de commits y la publicación de la rama y del Pull Request.

### Fase 2: Backend con Python 3.12 (COMPLETADA)

- **Objetivo:** preparar backend con FastAPI, configuración, modelos y pruebas.
- **Criterios de aceptación:**
  - [x] Python 3.12 verificado en el entorno local.
  - [x] Entorno virtual en `backend/.venv`.
  - [x] Estructura base FastAPI.
  - [x] Configuración con variables de entorno.
  - [x] API REST de ejecuciones.
  - [x] Pruebas automatizadas del backend.

### Fase 3: Infraestructura local Docker (COMPLETADA)

- **Objetivo:** orquestación local con Docker Compose, redes internas, volúmenes y health checks.
- **Criterios de aceptación:**
  - [x] `compose.yaml` con PostgreSQL, backend, n8n y Ollama.
  - [x] `backend/Dockerfile` con usuario no root y healthcheck.
  - [x] Red `postgres_net` para PostgreSQL y backend.
  - [x] Red `n8n_net` para n8n y backend.
  - [x] Red `ai_net` para Ollama y backend.
  - [x] Puertos publicados limitados a `127.0.0.1`.
  - [x] Volúmenes persistentes `postgres_data`, `n8n_data` y `ollama_data`.
  - [x] Health checks definidos.
  - [x] `docker compose config -q` validado.
  - [x] Imagen del backend construida; imágenes oficiales disponibles.
  - [x] Servicios arrancados.
  - [x] Conectividad entre contenedores verificada.

### Fase 4: Base de datos y migraciones (COMPLETADA)

- **Objetivo:** PostgreSQL, modelos base y Alembic.
- **Criterios de aceptación:**
  - [x] Modelos `Execution` y `AuditLog`.
  - [x] Migración inicial en Alembic.
  - [x] `backend/alembic/env.py` compatible con Windows y Docker.
  - [x] Migraciones aplicadas y verificadas en el contenedor.
  - [x] Migración `b7c1e4f2a9d3` aplicada con la restricción `ck_executions_status`.

### Fase 5: Proveedor de IA con Ollama (PENDIENTE)

- **Objetivo:** interfaz AIProvider configurable, implementación OllamaProvider y validación de salidas con esquemas explícitos.
- **Criterios de aceptación:**
  - [ ] Interfaz definida y desacoplada.
  - [ ] Conexión a `http://ollama:11434`.
  - [ ] Modelo `qwen2.5:3b-instruct` descargado en el volumen `ollama_data`.
  - [ ] Validación de respuestas contra esquema.
  - [ ] Logs sin secretos.
  - [ ] Compatibilidad de GPU comprobada o ejecución en CPU documentada.

### Fase 6: Integración n8n y flujos (PENDIENTE)

- **Objetivo:** flujos versionados en `n8n/`, integración con el backend y auditoría.
- **Criterios de aceptación:**
  - [ ] Flujos exportados en formato JSON.
  - [ ] Comunicación FastAPI -> n8n mediante `http://n8n:5678`.
  - [ ] Comunicación n8n -> FastAPI mediante `http://backend:8000`.
  - [ ] Integración documentada.
  - [ ] Registro de auditoría básico.

### Fase 7: Frontend Angular (PENDIENTE)

- **Objetivo:** aplicación Angular en modo estricto, comunicación únicamente con FastAPI.
- **Criterios de aceptación:**
  - [ ] Estructura base creada.
  - [ ] Comunicación HTTP con backend en `http://localhost:8000`.
  - [ ] Sin acceso directo a PostgreSQL, Ollama o n8n.
  - [ ] Orígenes CORS locales verificados.

### Fase 8: Pruebas, evaluación, limpieza y documentación final (PENDIENTE)

- **Objetivo:** pytest, Postman, `ai-eval/`, Pandas, hardening y documentación actualizada.
- **Criterios de aceptación:**
  - [x] Pruebas básicas ejecutadas y verificadas.
  - [ ] Colección Postman actualizada.
  - [ ] Casos de evaluación de IA definidos.
  - [ ] Documentación final de la fase completada.

## Notas

- No se marcarán tareas como completadas sin existencia de archivos o comprobaciones reales.
- Desarrollo fuera de `main`. Pull Request hacia `main`, sin fusionar automáticamente.
- Sin secretos en el repositorio.
- La infraestructura está arrancada y la migración `b7c1e4f2a9d3` está aplicada. No se ha descargado ningún modelo de Ollama ni se ha implementado la integración funcional FastAPI–n8n.
