# AI Automation Control Center

## Objetivo

AI Automation Control Center es una aplicación web local pensada como proyecto de cartera técnica. Su objetivo es demostrar la integración de automatización, inteligencia artificial local, tratamiento de datos, APIs, bases de datos y auditoría en un entorno reproducible y completamente local.

## Problema que resuelve

Permite automatizar flujos de trabajo que combinen extracción, validación y procesamiento de datos con modelos de IA locales, sin depender de servicios de pago ni de claves de API externas para la funcionalidad principal.

## Funcionalidades

### Previstas (no implementadas)
- Extracción y validación de facturas con IA local mediante Ollama.
- Limpieza y normalización de datos con Pandas.
- Orquestación de flujos con n8n autoalojado.
- Interfaz web con Angular para consulta de ejecuciones y auditoría.
- API REST con FastAPI.
- Almacenamiento persistente en PostgreSQL con trazabilidad.
- Migraciones con Alembic.
- Validación estricta de las salidas del modelo contra esquemas explícitos.
- Evaluación de prompts con casos deterministas.
- Pruebas automatizadas con pytest.
- Colección de API para pruebas con Postman.

### Implementadas
- Estructura base del repositorio y documentación inicial.
- Modelos `Execution` y `AuditLog` con migración inicial en Alembic.
- API REST de ejecuciones: creación, listado paginado, consulta por ID, cambio de estado y consulta de auditoría.
- Pruebas automatizadas del backend con pytest.

## Arquitectura y tecnologías

- **Frontend:** Angular con TypeScript en modo estricto
- **Backend:** FastAPI (Python 3.12)
- **Base de datos:** PostgreSQL
- **Automatización:** n8n autoalojado
- **IA local:** Ollama (modelo configurable, previsto qwen2.5:3b-instruct)
- **Migraciones:** Alembic
- **ORM:** SQLAlchemy
- **Validación:** Pydantic
- **Datos:** Pandas
- **Pruebas:** pytest
- **API testing:** Postman
- **Orquestación:** Docker Compose
- **Control de versiones:** Git y GitHub

Consulta docs/arquitectura.md para más detalles sobre componentes, comunicaciones y límites de seguridad.

## Requisitos previos

- Git
- Docker Desktop con contenedores Linux
- Node.js y npm
- Python 3.12 (el backend utiliza un entorno virtual propio en `backend/.venv`).
- Ollama instalado y accesible en http://localhost:11434
- Espacio suficiente en disco

## Configuración del entorno

1. Copiar `.env.example` a `.env` en la raíz del proyecto.
2. Ajustar los valores locales en `.env`. El archivo `.env` no se versiona.

Variables principales:

| Variable | Uso |
|---|---|
| `APP_ENV` | Entorno de ejecución (`dev` por defecto). |
| `TZ` | Zona horaria local (por defecto `Europe/Madrid`). |
| `DATABASE_URL` | Conexión a PostgreSQL usada por SQLAlchemy y Alembic. |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Credenciales de PostgreSQL para Docker Compose. |
| `BACKEND_HOST`, `BACKEND_PORT` | Dirección y puerto previstos para FastAPI. |
| `OLLAMA_BASE_URL`, `OLLAMA_MODEL` | Configuración de la IA local (integración pendiente). |
| `N8N_HOST`, `N8N_PORT`, `N8N_PROTOCOL`, `WEBHOOK_URL` | Dirección y URL local de n8n. |
| `N8N_ENCRYPTION_KEY` | Clave obligatoria para cifrar credenciales de n8n. No debe versionarse. |

> No se deben incluir credenciales reales en `.env.example` ni en archivos versionados.

## Estructura del repositorio

```
AI-AutomationControlCenter/
├── frontend/      # Aplicación Angular (pendiente)
├── backend/       # API FastAPI (en desarrollo)
├── database/      # Migraciones y datos de ejemplo
├── n8n/           # Exportaciones de flujos n8n
├── ai-eval/       # Casos de evaluación y conjuntos de prueba
├── postman/       # Colección Postman
├── infra/         # Configuración de infraestructura
├── docs/          # Documentación en español
├── AGENTS.md      # Instrucciones para agentes
├── .env.example   # Plantilla de variables de entorno (sin secretos)
├── .gitignore
├── LICENSE
└── README.md
```

## Puesta en marcha local

1. Copiar `.env.example` a `.env` y configurar los valores locales.
2. Crear el entorno virtual e instalar dependencias (ver sección siguiente).
3. Arrancar PostgreSQL con Docker Compose (ver sección de base de datos local).
4. Configurar la clave de n8n y arrancar el servicio (ver sección de n8n local).
5. Aplicar las migraciones con Alembic (ver sección de migraciones).
6. Iniciar el backend con Uvicorn.

El frontend, los flujos de n8n y la evaluación de prompts siguen pendientes. El servicio n8n ya está definido en Docker Compose, pero todavía no se comunica con FastAPI.

## Backend: ejecución y pruebas

Requisito: Python 3.12. Los comandos se ejecutan desde la raíz del proyecto en PowerShell.

```powershell
# Crear el entorno virtual e instalar dependencias de desarrollo
python -m venv backend/.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements-dev.txt
```

Ejecutar la API en modo desarrollo:

```powershell
$env:PYTHONPATH = "backend"
.\backend\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

La documentación interactiva queda en `http://127.0.0.1:8000/docs` y el esquema OpenAPI en `http://127.0.0.1:8000/openapi.json`.

Ejecutar las pruebas:

```powershell
.\backend\run-tests.ps1 -q
```

Ejecutar Ruff:

```powershell
.\backend\.venv\Scripts\ruff.exe check backend/app backend/tests
```

> `run-tests.ps1` utiliza automáticamente el intérprete de `backend/.venv`.

## Endpoints disponibles

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Información básica de la API. |
| GET | `/health` | Comprobación de salud. |
| POST | `/api/v1/executions/` | Crear una ejecución. |
| GET | `/api/v1/executions/` | Listar ejecuciones con paginación y filtros. |
| GET | `/api/v1/executions/{execution_id}` | Obtener una ejecución por ID. |
| PATCH | `/api/v1/executions/{execution_id}/status` | Cambiar el estado de una ejecución. |
| GET | `/api/v1/executions/{execution_id}/audit-logs` | Consultar los registros de auditoría. |

Estados permitidos: `pending`, `running`, `completed`, `failed` y `cancelled`. Transiciones válidas: `pending → running/cancelled` y `running → completed/failed/cancelled`.

La creación fija siempre `status="pending"` y `started_at`/`finished_at` en `null`; los campos gestionados por el servidor se ignoran si el cliente los envía. Cada creación y cada transición válida generan un registro de auditoría (`execution.created`, `execution.started`, `execution.completed`, `execution.failed` y `execution.cancelled`). Las transiciones rechazadas y las peticiones idempotentes sin cambio no generan nuevos registros.

## Estado real del desarrollo

- [x] Estructura de carpetas creada
- [x] Documentación base en español
- [x] Plantilla .env.example
- [x] .gitignore configurado
- [x] AGENTS.md versionado
- [x] Backend inicial (FastAPI, SQLAlchemy y Alembic)
- [x] Migraciones iniciales (Execution y AuditLog)
- [x] PostgreSQL con Docker Compose
- [x] Servicio n8n definido en Docker Compose (sin integración con el backend)
- [x] Pruebas automatizadas del backend
- [ ] Frontend implementado
- [ ] Flujos n8n e integración con el backend
- [ ] Evaluación de prompts y pruebas de calidad de IA

## Base de datos local (PostgreSQL con Docker Compose)

### Requisitos

- Docker Desktop instalado y en ejecución

### Preparación

1. Copiar `.env.example` a `.env` en la raíz del proyecto.
2. Configurar los valores de `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` y `DATABASE_URL` en `.env`.

### Validación

```powershell
docker compose config -q
```

### Arrancar PostgreSQL

```powershell
docker compose up -d postgres
```

### Comprobar estado

```powershell
docker compose ps
docker compose logs postgres
```

### Detener

```powershell
docker compose stop postgres
```

**Nota:** Los datos se guardan en el volumen postgres_data. No se recomienda eliminar el volumen en desarrollo a menos que se quiera borrar la base de datos completamente.

## n8n local (Docker Compose)

n8n se ejecuta en un contenedor independiente con su propia base SQLite dentro del volumen `n8n_data`. En esta etapa no se conecta a PostgreSQL, FastAPI ni Ollama. El puerto solo se publica en la interfaz local `127.0.0.1:5678`.

### Aislamiento de red y endurecimiento

- PostgreSQL usa la red exclusiva `postgres_net`; n8n usa la red exclusiva `n8n_net`. No comparten red, por lo que n8n no puede resolver ni alcanzar `postgres` mediante el DNS interno de Docker.
- Los puertos publicados se mantienen sin cambios y limitados a la interfaz local: PostgreSQL en `127.0.0.1:5432` y n8n en `127.0.0.1:5678`. FastAPI, ejecutándose en Windows, sigue accediendo a PostgreSQL mediante `localhost:5432`.
- `N8N_BLOCK_ENV_ACCESS_IN_NODE=true` impide que las expresiones y los nodos Code accedan a las variables de entorno del contenedor, incluida la clave de cifrado.
- Las redes no se marcan como `internal: true`; se mantienen como redes bridge locales para no bloquear el acceso desde el host ni la conectividad saliente que n8n pueda necesitar.
- La futura comunicación de n8n hacia FastAPI podrá usar `host.docker.internal`; no está implementada en esta etapa.

### Configurar la clave de cifrado

`N8N_ENCRYPTION_KEY` protege las credenciales guardadas por n8n. Compose la exige y no tiene valor por defecto. Genera una clave aleatoria desde PowerShell:

```powershell
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$key = New-Object byte[] 32
$rng.GetBytes($key)
[Convert]::ToBase64String($key)
```

Copia el resultado en `N8N_ENCRYPTION_KEY` dentro de `.env`. No la subas a Git ni reutilices el marcador de `.env.example`. Conserva la misma clave mientras exista el volumen `n8n_data`: si la cambias, n8n no podrá descifrar las credenciales anteriores.

### Arrancar n8n

```powershell
docker compose up -d n8n
docker compose ps n8n
docker compose logs -f n8n
```

Abre `http://127.0.0.1:5678` cuando el servicio esté listo. Si `N8N_ENCRYPTION_KEY` no está definida o está vacía en `.env`, Compose aborta el arranque de forma intencionada.

### Comprobar disponibilidad

```powershell
Invoke-WebRequest http://127.0.0.1:5678/healthz -UseBasicParsing
```

También puedes usar `curl.exe -fsS http://127.0.0.1:5678/healthz`. El servicio puede tardar unos segundos en completar el arranque; `docker compose ps n8n` muestra su estado de salud.

### Detener sin perder datos

```powershell
docker compose stop n8n
```

Para detener todos los servicios sin borrar datos:

```powershell
docker compose down
```

No ejecutes `docker compose down -v`: eliminaría los volúmenes `n8n_data` y `postgres_data`. El volumen de n8n es independiente del volumen de PostgreSQL.

### Notas de seguridad y desarrollo

- n8n se publica exclusivamente en `127.0.0.1:5678`.
- La configuración usa HTTP local y `N8N_SECURE_COOKIE=false`; no debe reutilizarse así en un entorno expuesto a la red.
- La integración entre FastAPI y n8n se abordará en una etapa posterior.

## Migraciones con Alembic

Con PostgreSQL en ejecución y `DATABASE_URL` configurada en `.env`, desde la raíz del proyecto:

```powershell
# Aplicar todas las migraciones pendientes
.\backend\.venv\Scripts\python.exe -m alembic -c backend/alembic.ini upgrade head

# Consultar la revisión aplicada
.\backend\.venv\Scripts\python.exe -m alembic -c backend/alembic.ini current
```

## Licencia

Ver archivo LICENSE.
