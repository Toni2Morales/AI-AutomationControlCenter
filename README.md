# AI Automation Control Center

## Objetivo

AI Automation Control Center es una aplicación web local pensada como proyecto de cartera técnica. Su objetivo es demostrar la integración de automatización, inteligencia artificial local, tratamiento de datos, APIs, bases de datos y auditoría en un entorno reproducible y completamente local.

## Problema que resuelve

Permite automatizar flujos de trabajo que combinen extracción, validación y procesamiento de datos con modelos de IA locales, sin depender de servicios de pago ni de claves de API externas para la funcionalidad principal.

## Funcionalidades

### Implementadas

- Estructura base del repositorio y documentación inicial.
- Modelos `Execution` y `AuditLog` con migración inicial en Alembic.
- API REST de ejecuciones: creación, listado paginado, consulta por ID, cambio de estado y consulta de auditoría.
- Pruebas automatizadas del backend con pytest.
- Infraestructura Docker operativa para FastAPI, PostgreSQL, n8n y Ollama.
- Redes separadas para PostgreSQL, n8n y Ollama.
- Volúmenes persistentes para PostgreSQL, n8n y Ollama.
- Configuración CORS para el futuro frontend Angular local.

### Validado

- Imagen del backend construida y servicio `backend` ejecutándose con usuario no root.
- Servicios PostgreSQL, backend, n8n y Ollama arrancados y en estado `healthy`.
- `docker compose config -q` validado correctamente.
- Puertos publicados exclusivamente en `127.0.0.1`; Ollama no publica puertos.
- Conectividad interna comprobada entre backend, n8n, Ollama y PostgreSQL.
- Migración `b7c1e4f2a9d3` aplicada, con la restricción `ck_executions_status` activa.
- Suite del backend ejecutada: 78 pruebas superadas y 0 fallidas.
- Consulta `GET /api/v1/executions/?page=1&page_size=20` verificada contra PostgreSQL.

### Previstas (no implementadas)

- Interfaz web con Angular para consulta de ejecuciones y auditoría.
- Integración funcional entre FastAPI y n8n.
- Extracción y validación de facturas con IA local mediante Ollama.
- Limpieza y normalización de datos con Pandas.
- Evaluación de prompts con casos deterministas.
- Colección de API para pruebas con Postman.

## Arquitectura y tecnologías

- **Frontend:** Angular con TypeScript en modo estricto (pendiente).
- **Backend:** FastAPI (Python 3.12), ejecutado en Docker.
- **Base de datos:** PostgreSQL, ejecutado en Docker.
- **Automatización:** n8n autoalojado, ejecutado en Docker.
- **IA local:** Ollama, ejecutado en Docker.
- **Migraciones:** Alembic.
- **ORM:** SQLAlchemy.
- **Validación:** Pydantic.
- **Datos:** Pandas.
- **Pruebas:** pytest.
- **API testing:** Postman.
- **Orquestación:** Docker Compose.
- **Control de versiones:** Git y GitHub.

Consulta `docs/arquitectura.md` para más detalles sobre componentes, comunicaciones y límites de seguridad.

## Requisitos previos

- Git.
- Docker Desktop con contenedores Linux.
- Node.js y npm para el futuro frontend Angular.
- Python 3.12 para ejecutar las pruebas del backend en Windows.
- Espacio suficiente en disco para las imágenes y los modelos de Ollama.

Ollama se ejecuta dentro de Docker. No es necesario tener Ollama en ejecución en Windows para esta arquitectura. La instalación existente en Windows no se modifica ni se elimina.

## Configuración del entorno

1. Copiar `.env.example` a `.env` en la raíz del proyecto.
2. Ajustar los valores locales en `.env`. El archivo `.env` no se versiona.

Variables principales:

| Variable | Uso |
|---|---|
| `APP_ENV` | Entorno de ejecución (`dev` por defecto). |
| `APP_NAME` | Nombre de la aplicación. |
| `TZ` | Zona horaria local (por defecto `Europe/Madrid`). |
| `BACKEND_PORT` | Puerto publicado en Windows. Uvicorn escucha en `0.0.0.0:8000` dentro del contenedor. |
| `BACKEND_CORS_ORIGINS` | Orígenes permitidos para Angular, separados por comas. |
| `DATABASE_URL` | URL interna a PostgreSQL con host `postgres`. Dentro de Docker, Compose construye la variable del backend a partir de `POSTGRES_*`; para Alembic desde Windows se sobrescribe temporalmente con `127.0.0.1` (ver Migraciones). |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Credenciales de PostgreSQL para Docker Compose. La contraseña local debe usar solo caracteres URL-safe: letras ASCII, dígitos, `_` y `-`. |
| `POSTGRES_HOST`, `POSTGRES_PORT` | Valores de referencia del puerto publicado para herramientas ejecutadas en Windows; no construyen `DATABASE_URL` automáticamente. |
| `OLLAMA_IMAGE` | Imagen oficial de Ollama; valor por defecto fijado: `ollama/ollama:0.40.15`. |
| `OLLAMA_BASE_URL` | URL interna de Ollama: `http://ollama:11434`. |
| `OLLAMA_MODEL`, `OLLAMA_TIMEOUT` | Modelo previsto y tiempo máximo de espera de la integración de IA. |
| `N8N_HOST`, `N8N_PORT`, `N8N_PROTOCOL`, `WEBHOOK_URL` | Dirección y URL local de n8n. |
| `N8N_BASE_URL` | URL interna prevista para que el backend llame a n8n: `http://n8n:5678`. |
| `N8N_CALLBACK_BASE_URL` | URL interna prevista para que n8n llame a FastAPI: `http://backend:8000`. La integración todavía no la utiliza. |
| `N8N_ENCRYPTION_KEY` | Clave obligatoria para cifrar credenciales de n8n. No debe versionarse. |
| `LOG_LEVEL` | Nivel de registro de n8n; se aplica como `N8N_LOG_LEVEL`. FastAPI no lo consume actualmente. |

> No se deben incluir credenciales reales en `.env.example` ni en archivos versionados.

## Estructura del repositorio

```text
AI-AutomationControlCenter/
├── backend/
│   ├── app/                 # API FastAPI
│   ├── alembic/             # Migraciones
│   ├── tests/               # Pruebas automatizadas
│   ├── Dockerfile           # Imagen del backend
│   ├── .dockerignore
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── run-tests.ps1
├── docs/                    # Documentación en español
├── compose.yaml             # Servicios, redes y volúmenes
├── .env.example             # Plantilla de variables sin secretos
├── .gitignore
├── AGENTS.md
├── LICENSE
└── README.md
```

El frontend Angular todavía no existe en el repositorio.

## Puesta en marcha local

1. Copiar `.env.example` a `.env` y configurar los valores locales.
2. Validar la configuración de Compose.
3. Construir y arrancar PostgreSQL, FastAPI, n8n y Ollama.
4. Aplicar las migraciones de Alembic.
5. Consultar la API en `http://127.0.0.1:8000/docs`.
6. Abrir n8n en `http://127.0.0.1:5678`.

```powershell
docker compose config -q
docker compose up -d postgres backend n8n ollama
docker compose run --rm backend alembic -c /app/alembic.ini upgrade head
docker compose ps
```

La primera puesta en marcha descarga las imágenes y puede tardar. La descarga del modelo de Ollama se realiza en una fase posterior.

## Servicios Docker

| Servicio | Imagen o construcción | Redes | Puerto en Windows | Persistencia |
|---|---|---|---|---|
| `postgres` | `postgres:16` | `postgres_net` | `127.0.0.1:5432` | `postgres_data` |
| `backend` | `backend/Dockerfile` | `postgres_net`, `n8n_net`, `ai_net` | `127.0.0.1:8000` | Sin volumen; es stateless |
| `n8n` | `n8nio/n8n:2.47.2` | `n8n_net` | `127.0.0.1:5678` | `n8n_data` |
| `ollama` | `ollama/ollama:0.40.15` (configurable con `OLLAMA_IMAGE`) | `ai_net` | Ninguno | `ollama_data` |

### Redes y comunicaciones internas

- `postgres_net` solo contiene `postgres` y `backend`.
- `n8n_net` solo contiene `n8n` y `backend`.
- `ai_net` solo contiene `ollama` y `backend`.
- n8n no pertenece a `postgres_net`, por lo que no puede resolver ni alcanzar PostgreSQL.
- PostgreSQL no pertenece a `n8n_net` ni a `ai_net`.
- Ollama no pertenece a `postgres_net` ni a `n8n_net`.
- El backend usa `postgres:5432`, `n8n:5678` y `ollama:11434`.
- n8n puede llamar al backend mediante `http://backend:8000`.
- Los nombres DNS internos son los nombres de servicio de Compose.

Los puertos publicados se enlazan exclusivamente a `127.0.0.1`. No se publica ningún servicio en `0.0.0.0` ni se abre ningún puerto en el router.

## Backend: Docker, ejecución y pruebas

El backend se construye desde `backend/Dockerfile`:

- Python 3.12 sobre una imagen `slim`.
- Dependencias de producción de `backend/requirements.txt`.
- Usuario no root.
- Uvicorn escuchando en `0.0.0.0:8000` dentro del contenedor.
- Healthcheck contra `http://127.0.0.1:8000/health`.
- Alembic incluido para ejecutar migraciones desde el contenedor.
- Sin `.env`, `.venv`, secretos ni cachés en la imagen.

Comandos de operación:

```powershell
# Construir la imagen (no arranca servicios)
docker compose build backend

# Arrancar el backend
docker compose up -d backend

# Ver registros
docker compose logs -f backend

# Comprobar salud
Invoke-WebRequest http://127.0.0.1:8000/health -UseBasicParsing
```

### Pruebas en Windows

La suite completa se ejecuta con el entorno virtual local. El script configura `PYTHONPATH` automáticamente:

```powershell
.\backend\run-tests.ps1 -q
```

Las pruebas de concurrencia usan Testcontainers y crean un contenedor PostgreSQL efímero aislado. Requieren Docker disponible. Para ejecutar únicamente las pruebas que no necesitan contenedores:

```powershell
.\backend\run-tests.ps1 -q --ignore=backend/tests/test_executions_concurrency.py
```

Ejecutar Ruff:

```powershell
.\backend\.venv\Scripts\ruff.exe check backend/app backend/tests backend/alembic/env.py
```

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

## PostgreSQL

PostgreSQL se ejecuta en `postgres:16` y conserva sus datos en el volumen `postgres_data`. El puerto se publica únicamente en `127.0.0.1:5432` para herramientas lanzadas desde Windows.

El backend accede a PostgreSQL por la red interna. Docker Compose construye la URL del backend a partir de `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` y el host `postgres`:

```text
postgresql+psycopg://USUARIO:CONTRASEÑA@postgres:5432/BASE_DE_DATOS
```

La plantilla `.env.example` mantiene `DATABASE_URL` con host `postgres`. Docker Compose no reutiliza ese valor para el contenedor: construye su propia variable a partir de `POSTGRES_*`. No se debe usar `127.0.0.1` dentro del contenedor del backend, porque esa dirección apunta al propio contenedor.

Con la implementación actual, `POSTGRES_PASSWORD` debe contener únicamente caracteres URL-safe: letras ASCII mayúsculas y minúsculas, dígitos, guion bajo (`_`) y guion (`-`). Compose interpola la contraseña directamente en `DATABASE_URL`; caracteres reservados como `@`, `:`, `/`, `?`, `#` o `%` pueden alterar la URL. Esta es una restricción de la configuración actual, no una limitación inherente a PostgreSQL. Si en el futuro se necesitan contraseñas arbitrarias, la URL deberá construirse con `sqlalchemy.engine.URL.create()` a partir de componentes separados, pasando la contraseña original sin percent-encoding manual.

Desde Windows, el puerto publicado es `127.0.0.1:5432`. Con la plantilla tal cual, las herramientas que lean `.env` desde Windows verán el host `postgres`, que no resuelve. Para usar Alembic directamente en Windows hay que sobrescribir `DATABASE_URL` en la sesión de PowerShell; el procedimiento está en la sección de migraciones.

Comandos útiles:

```powershell
docker compose up -d postgres
docker compose ps postgres
docker compose logs postgres
docker compose exec postgres psql -U aacc_user -d aacc_db
```

No ejecutes `docker compose down -v`: eliminaría los volúmenes `postgres_data`, `n8n_data` y `ollama_data`.

## n8n

n8n se ejecuta en un contenedor independiente con su base SQLite dentro del volumen `n8n_data`. No se conecta a PostgreSQL ni a Ollama.

- `N8N_BLOCK_ENV_ACCESS_IN_NODE=true` impide que las expresiones y los nodos Code accedan a las variables de entorno del contenedor.
- `N8N_ENCRYPTION_KEY` se obtiene de `.env` y no tiene valor por defecto.
- La clave debe conservarse mientras exista `n8n_data`.
- n8n comparte `n8n_net` únicamente con el backend.
- La futura comunicación de n8n hacia FastAPI usará `http://backend:8000`.
- La comunicación del backend hacia n8n usará `http://n8n:5678`.
- La integración funcional entre ambos servicios está pendiente.

Configurar la clave de cifrado:

```powershell
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
$key = New-Object byte[] 32
$rng.GetBytes($key)
[Convert]::ToBase64String($key)
```

Copia el resultado en `N8N_ENCRYPTION_KEY` dentro de `.env`. No la subas a Git ni reutilices el marcador de `.env.example`.

Arrancar y comprobar n8n:

```powershell
docker compose up -d n8n
docker compose ps n8n
Invoke-WebRequest http://127.0.0.1:5678/healthz -UseBasicParsing
```

## Ollama

Ollama se ejecuta en Docker mediante la imagen oficial configurada en `OLLAMA_IMAGE`. No publica ningún puerto en Windows y solo comparte la red `ai_net` con el backend.

- El backend usa `http://ollama:11434`.
- Los modelos se guardan en el volumen `ollama_data`.
- La integración funcional con el backend está pendiente.
- No se ha configurado GPU.
- La compatibilidad de GPU con Docker Desktop y WSL2 debe comprobarse antes de activarla. Si no está disponible, Ollama puede ejecutarse en CPU.

Cuando se autorice la descarga del modelo, el comando previsto es:

```powershell
docker compose exec ollama ollama pull qwen2.5:3b-instruct
docker compose exec ollama ollama list
```

No se ha descargado ningún modelo en esta fase.

## Migraciones con Alembic

La imagen del backend incluye `alembic`, `alembic.ini` y el directorio `backend/alembic`. `backend/alembic/env.py` calcula la raíz del proyecto a partir de su propia ruta, por lo que funciona tanto desde Windows como dentro del contenedor.

### Dentro de Docker (método principal)

Con PostgreSQL en ejecución:

```powershell
# Aplicar todas las migraciones pendientes
docker compose run --rm backend alembic -c /app/alembic.ini upgrade head

# Consultar la revisión aplicada
docker compose run --rm backend alembic -c /app/alembic.ini current
```

También se puede ejecutar sobre un backend ya arrancado:

```powershell
docker compose exec backend alembic -c /app/alembic.ini upgrade head
```

Dentro de Docker, `DATABASE_URL` apunta a `postgres:5432`. La revisión actual es `b7c1e4f2a9d3` (`head`) y la restricción `ck_executions_status` ya está aplicada; no hay migraciones pendientes en este momento.

### Desde Windows (alternativa)

La vía principal recomendada es ejecutar Alembic desde el contenedor backend. Este procedimiento es una alternativa válida para herramientas locales. `backend/alembic/env.py` usa `settings.DATABASE_URL`. `pydantic-settings` da prioridad a la variable de entorno sobre el valor de `.env`, por lo que se puede usar una sobrescritura temporal sin editar `.env`:

```powershell
# Solo para esta sesión de PowerShell.
# Sustituye USUARIO, CONTRASENA y BASE_DE_DATOS por los valores locales.
$env:DATABASE_URL = "postgresql+psycopg://USUARIO:CONTRASENA@127.0.0.1:5432/BASE_DE_DATOS"
.\backend\.venv\Scripts\python.exe -m alembic -c backend/alembic.ini current
.\backend\.venv\Scripts\python.exe -m alembic -c backend/alembic.ini upgrade head
Remove-Item Env:DATABASE_URL
```

`Remove-Item Env:DATABASE_URL` elimina la sobrescritura de la sesión; después, los comandos vuelven a leer `.env`. La sobrescritura afecta únicamente a esa sesión de PowerShell y no modifica `.env`. La contraseña local debe ser URL-safe (letras ASCII, dígitos, `_` y `-`), de modo que la misma contraseña funcione tanto en Compose como en esta alternativa. Si en el futuro se necesitan contraseñas arbitrarias, se deberá construir la URL con `sqlalchemy.engine.URL.create()` a partir de componentes separados. No copies credenciales reales a la documentación ni a archivos versionados.

## Angular

Angular se ejecutará en Windows y se comunicará exclusivamente con FastAPI en `http://localhost:8000`. No accederá directamente a PostgreSQL, n8n ni Ollama.

FastAPI permite los orígenes locales configurados en `BACKEND_CORS_ORIGINS`. Cuando exista el frontend, se puede usar además un proxy de desarrollo de Angular para evitar problemas de CORS.

## Estado real del desarrollo

- [x] Estructura de carpetas creada
- [x] Documentación base en español
- [x] Plantilla `.env.example`
- [x] `.gitignore` configurado
- [x] `AGENTS.md` versionado
- [x] Backend inicial (FastAPI, SQLAlchemy y Alembic)
- [x] Migraciones iniciales (Execution y AuditLog)
- [x] PostgreSQL con Docker Compose
- [x] Servicio n8n definido en Docker Compose (sin integración con el backend)
- [x] Pruebas automatizadas del backend
- [x] Dockerfile del backend y `.dockerignore`
- [x] Servicio backend en Docker Compose
- [x] Servicio Ollama en Docker Compose con volumen `ollama_data`
- [x] Redes `postgres_net`, `n8n_net` y `ai_net`
- [x] Configuración CORS para Angular local
- [x] Imagen del backend construida
- [x] Servicios PostgreSQL, backend, n8n y Ollama arrancados y saludables
- [x] Conectividad interna de la infraestructura verificada
- [x] Migración `b7c1e4f2a9d3` aplicada y verificada
- [ ] Modelo de Ollama descargado
- [ ] Frontend implementado
- [ ] Flujos n8n e integración con el backend
- [ ] Evaluación de prompts y pruebas de calidad de IA

## Licencia

Ver archivo LICENSE.
