# Arquitectura

## Visión general

AI Automation Control Center es una aplicación **local-first**. Todos los componentes se ejecutan en el entorno local. El frontend **únicamente** se comunica con el backend. El backend actúa como frontera única: es el único componente que accede a PostgreSQL, n8n y Ollama.

FastAPI, PostgreSQL, n8n y Ollama se ejecutan en Docker Desktop sobre Windows. Angular se ejecutará en Windows y accederá a FastAPI mediante un puerto publicado exclusivamente en `127.0.0.1`.

## Componentes y responsabilidades

| Componente | Tecnología | Dónde se ejecuta | Responsabilidad | Acceso |
|---|---|---|---|---|
| **Frontend** | Angular + TypeScript en modo estricto | Windows | Interfaz de usuario para subir archivos, consultar ejecuciones, ver resultados y auditoría. | Solo HTTP REST hacia el backend. |
| **Backend** | FastAPI (Python 3.12) | Docker | Lógica de negocio, validación, orquestación, auditoría y punto único de acceso. La interfaz de proveedor de IA está prevista para la Fase 5. | PostgreSQL, n8n y Ollama por redes internas. |
| **Base de datos** | PostgreSQL | Docker | Almacenamiento persistente, trazabilidad, auditoría y registros de ejecución. | **Solo** desde el backend. |
| **Automatización** | n8n autoalojado | Docker | Orquestación de flujos de trabajo. Puede invocar al backend. | Solo por `n8n_net`; sin acceso a PostgreSQL. |
| **IA local** | Ollama | Docker | Inferencia local con modelos configurables. | **Solo** desde el backend por `ai_net`. |
| **Orquestación** | Docker Compose | Windows | Levantamiento local, redes internas, volúmenes persistentes, orden de arranque y comprobaciones de salud. | Local. |

## Diagrama de comunicaciones

```text
┌──────────────────────────── Windows ────────────────────────────┐
│                                                                 │
│  Angular :4200                                                  │
│      │                                                          │
│      │ http://localhost:8000                                    │
│      ▼                                                          │
│  127.0.0.1:8000                                                 │
│                                                                 │
└──────┼──────────────────────────────────────────────────────────┘
       │
┌──────┼──────────────────────── Docker Desktop ──────────────────┐
│      ▼                                                          │
│  ┌───────────┐                                                  │
│  │  backend  │                                                  │
│  │  FastAPI  │                                                  │
│  │   :8000   │                                                  │
│  └─────┬─────┘                                                  │
│        │                                                        │
│  ┌─────┴──────────────┬─────────────────────┐                   │
│  │                    │                     │                   │
│  ▼                    ▼                     ▼                   │
│ postgres_net        n8n_net               ai_net                 │
│  │                    │                     │                   │
│  ▼                    ▼                     ▼                   │
│ ┌──────────┐      ┌──────────┐         ┌──────────┐             │
│ │ postgres │      │   n8n    │         │  ollama  │             │
│ │  :5432   │      │  :5678   │         │  :11434  │             │
│ └──────────┘      └────┬─────┘         └──────────┘             │
│                        │                                        │
│                        │ http://backend:8000                    │
│                        └───────────────> backend                │
│                                                                 │
│  n8n no está en postgres_net ni en ai_net.                      │
└─────────────────────────────────────────────────────────────────┘
```

## Redes Docker

| Red | Servicios | Propósito |
|---|---|---|
| `postgres_net` | `postgres`, `backend` | Acceso exclusivo del backend a PostgreSQL. |
| `n8n_net` | `n8n`, `backend` | Comunicación bidireccional entre FastAPI y n8n. |
| `ai_net` | `ollama`, `backend` | Acceso exclusivo del backend a Ollama. |

Resultados:

- PostgreSQL no comparte red con n8n ni con Ollama.
- n8n no puede resolver ni alcanzar `postgres`.
- Ollama no puede resolver ni alcanzar PostgreSQL ni n8n.
- El backend puede resolver `postgres`, `n8n` y `ollama`.
- n8n puede resolver `backend`.
- Las comunicaciones internas usan los nombres de servicio de Compose.

Las redes se mantienen como redes bridge locales, no como `internal: true`, para conservar el acceso desde el host y permitir la descarga de imágenes y modelos cuando sea necesario.

## Puertos publicados

| Servicio | Enlace en Windows | Exposición |
|---|---|---|
| `backend` | `127.0.0.1:8000` | Solo loopback local. |
| `n8n` | `127.0.0.1:5678` | Solo loopback local. |
| `postgres` | `127.0.0.1:5432` | Solo loopback local, para herramientas desde Windows. |
| `ollama` | Sin puerto publicado | Solo accesible desde `ai_net`. |

Ningún servicio se publica en `0.0.0.0`. No se abre ningún puerto en el router ni se modifica el firewall.

## Comunicaciones

| Origen | Destino | URL |
|---|---|---|
| Angular | FastAPI | `http://localhost:8000` |
| FastAPI | PostgreSQL | `postgresql+psycopg://...@postgres:5432/...` |
| FastAPI | n8n | `http://n8n:5678` |
| n8n | FastAPI | `http://backend:8000` |
| FastAPI | Ollama | `http://ollama:11434` |
| Angular | PostgreSQL, n8n u Ollama | Prohibido |

## Persistencia

| Volumen | Servicio | Contenido |
|---|---|---|
| `postgres_data` | `postgres` | Base de datos PostgreSQL. |
| `n8n_data` | `n8n` | Base SQLite, workflows y credenciales cifradas de n8n. |
| `ollama_data` | `ollama` | Modelos descargados por Ollama. |

El backend no usa volumen porque es stateless. Los volúmenes existentes se conservan. No se debe ejecutar `docker compose down -v` salvo que se quiera eliminar toda la persistencia.

## Migraciones

La vía principal recomendada para ejecutar Alembic es el contenedor del backend:

```powershell
docker compose run --rm backend alembic -c /app/alembic.ini upgrade head
```

`backend/alembic/env.py` calcula la raíz del proyecto desde la ubicación del propio archivo, por lo que las rutas funcionan tanto en Windows como dentro de la imagen. También es posible ejecutar Alembic desde Windows; en ese caso hay que sobrescribir temporalmente `DATABASE_URL` con el host `127.0.0.1` en la sesión de PowerShell, sin modificar `.env`. El procedimiento completo está en el README.

## Límites de seguridad

- El frontend **no** accede directamente a PostgreSQL, Ollama ni n8n.
- PostgreSQL y n8n **no** se exponen a redes públicas.
- Ollama no publica puertos en Windows.
- Todos los puertos publicados se limitan a `127.0.0.1`.
- El backend es el único componente con acceso a las tres redes internas.
- n8n no tiene acceso directo a PostgreSQL.
- Las salidas del modelo de IA se validarán contra esquemas explícitos.
- El modelo se configurará mediante variables de entorno y una interfaz de proveedor que se implementará en la Fase 5.
- Los secretos se gestionan con `.env` fuera de control de versiones.
- El contenedor del backend se ejecuta con un usuario no root.
- No se utilizan `network_mode: host`, `privileged: true` ni el socket de Docker.

## Principios arquitectónicos

- **Local-first:** sin dependencia de servicios de pago para la funcionalidad principal.
- **Frontera única:** el backend es el punto de control.
- **Abstracción de IA (prevista):** en la Fase 5 se implementarán la interfaz `AIProvider` y la implementación `OllamaProvider`. La infraestructura Ollama y la URL interna ya están desplegadas, pero la integración funcional todavía no existe.
- **Validación estricta:** respuestas del modelo validadas, errores controlados y registrados.
- **Trazabilidad y auditoría:** registros de ejecución, errores y cambios relevantes.
- **Seguridad por defecto:** sin credenciales en código, sin exposición pública, acceso restringido entre servicios.
- **Reproducible:** entorno local documentado.

## Estado

### Implementado

- Infraestructura Docker definida en `compose.yaml` y `backend/Dockerfile`.
- Backend FastAPI con API REST de ejecuciones, modelos `Execution` y `AuditLog`, y migraciones de Alembic.
- Redes separadas `postgres_net`, `n8n_net` y `ai_net`.
- Volúmenes persistentes `postgres_data`, `n8n_data` y `ollama_data`.
- Configuración CORS para el futuro frontend Angular local.

### Validado

- Imagen del backend construida y servicio `backend` ejecutándose con usuario no root.
- Servicios PostgreSQL, backend, n8n y Ollama arrancados y en estado `healthy`.
- Puertos publicados exclusivamente en `127.0.0.1`; Ollama no publica puertos.
- Conectividad interna comprobada entre backend, n8n, Ollama y PostgreSQL.
- Migración `b7c1e4f2a9d3` aplicada, con la restricción `ck_executions_status` activa.
- `docker compose config -q` validado correctamente.
- Suite del backend ejecutada: 78 pruebas superadas y 0 fallidas.

### Pendiente

- Integración funcional entre FastAPI y n8n.
- Proveedor de IA y conexión funcional con Ollama.
- Modelo de Ollama descargado.
- Importación y tratamiento de facturas con Pandas.
- Evaluación de prompts y pruebas de calidad de IA.
- Frontend Angular y colección de Postman.
