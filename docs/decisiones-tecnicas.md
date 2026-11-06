# Decisiones técnicas

## Decisiones confirmadas

| Decisión | Motivo |
|---|---|
| **Frontend: Angular + TypeScript en modo estricto** | Estructura sólida, tipado fuerte, buen para portfolio profesional. |
| **Backend: FastAPI (Python)** | Rápido para APIs REST, validación con Pydantic, documentación automática, ideal para integrar IA. |
| **Python 3.12 (objetivo)** | Versión estable objetivo. Usar entorno virtual propio. Si no está instalado, documentar requisito sin instalar globalmente. |
| **Base de datos: PostgreSQL** | Robusto, relacional, ampliamente usado, buen para trazabilidad/auditoría. |
| **Automatización: n8n autoalojado** | Permite orquestar flujos localmente, exportar flujos como JSON versionados. |
| **n8n: imagen fijada y volumen propio** | Se fija una versión estable explícita, se publica solo en `127.0.0.1:5678` y se usa el volumen `n8n_data` para su SQLite interno. Sin conexión a PostgreSQL ni al backend en esta fase. |
| **Redes Docker separadas** | PostgreSQL usa `postgres_net` y n8n usa `n8n_net`; no comparten red. Los puertos se mantienen en `127.0.0.1` para conservar el acceso desde Windows. |
| **n8n: bloqueo de variables de entorno en nodos** | `N8N_BLOCK_ENV_ACCESS_IN_NODE=true` evita que expresiones y nodos Code lean variables del contenedor, incluida la clave de cifrado. |
| **IA local: Ollama** | Funciona 100% local, sin claves de pago para funcionalidad principal. |
| **Modelo inicial: qwen2.5:3b-instruct** | Equilibrio razonable entre tamaño, rendimiento en CPU/GPU modesta (GTX 960) y capacidad para extracción/JSON. Configurable. |
| **Proveedor IA configurable (interfaz)** | Permite cambiar modelo/proveedor sin reescribir lógica de negocio. |
| **Docker Compose** | Orquestación local reproducible. |
| **Migraciones: Alembic** | Versionado de esquema PostgreSQL. |
| **Concurrencia de ejecuciones: `SELECT ... FOR UPDATE`** | Serializa las transiciones por fila en PostgreSQL y evita carreras entre estados y auditoría. |
| **Restricción `CHECK` de estados** | La base de datos solo admite `pending`, `running`, `completed`, `failed` y `cancelled`. |
| **Pruebas backend: pytest** | Estándar en Python. |
| **Pruebas de concurrencia: PostgreSQL con Testcontainers** | Usan un contenedor efímero aislado; no reutilizan la base local ni sus volúmenes. El puerto se publica solo en `127.0.0.1` con asignación aleatoria de Docker. |
| **Pruebas API: Postman** | Documentación y pruebas manuales/automatizables. |
| **Control de versiones: Git + GitHub** | Trazabilidad, ramas, PRs. |
| **Idioma español** | Toda documentación dirigida a personas en español. Código en inglés por convención. |
| **Backend como frontera** | Frontend NO accede directo a DB/Ollama/n8n. Solo vía API backend. |
| **Validación estricta salidas IA** | Usar esquemas/Pydantic, rechazar respuestas malformadas, registrar errores. |
| **Local-first sin claves pago** | Objetivo del portfolio. |
| **Ramas y PRs** | Nunca trabajar en main, usar feat/fix/docs/test/chore, PR hacia main sin merge automático. |
| **AGENTS.md versionado** | Instrucciones persistentes para agentes, visibles en repo. |

## Notas
- Ollama se ejecuta fuera de Docker inicialmente en Windows.
- Las direcciones entre servicios se configuran explícitamente.
- Sin secretos en código/versionado.
- `N8N_ENCRYPTION_KEY` se obtiene de `.env`, no tiene valor por defecto y debe conservarse mientras exista el volumen `n8n_data`.
- n8n usa HTTP local con `N8N_SECURE_COOKIE=false`; esta configuración es solo para desarrollo en `127.0.0.1`.
- n8n y PostgreSQL usan redes Docker exclusivas. FastAPI en Windows mantiene el acceso a PostgreSQL por `localhost:5432`; n8n se publica en `127.0.0.1:5678`.
- La futura comunicación n8n -> FastAPI podrá usar `host.docker.internal`; no está implementada en esta etapa.
- Las redes no se configuran como `internal: true`; se mantienen como redes bridge locales para preservar el acceso desde el host.
- Las transiciones de `Execution` se serializan con bloqueo pesimista por fila. SQLite se usa para pruebas de lógica y atomicidad, no como evidencia de concurrencia real.
- Las pruebas de concurrencia requieren Docker y Testcontainers. Si falta Testcontainers, la importación falla de forma visible; si Docker no está disponible, el preflight omite explícitamente las pruebas en lugar de simular un resultado.
- El contenedor PostgreSQL efímero de pruebas se publica únicamente en `127.0.0.1` y utiliza un puerto libre asignado por Docker.
