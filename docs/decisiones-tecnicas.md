# Decisiones técnicas

## Decisiones confirmadas

| Decisión | Motivo |
|---|---|
| **Frontend: Angular + TypeScript en modo estricto** | Estructura sólida, tipado fuerte, buen para portfolio profesional. |
| **Backend: FastAPI (Python)** | Rápido para APIs REST, validación con Pydantic, documentación automática, ideal para integrar IA. |
| **Python 3.12 (objetivo)** | Versión estable objetivo. El backend se ejecuta en Docker; el entorno virtual local se conserva para pruebas y herramientas. |
| **Base de datos: PostgreSQL** | Robusto, relacional, ampliamente usado, buen para trazabilidad/auditoría. |
| **Automatización: n8n autoalojado** | Permite orquestar flujos localmente, exportar flujos como JSON versionados. |
| **Backend en Docker** | FastAPI se ejecuta en la misma red interna que PostgreSQL, n8n y Ollama. Angular queda fuera de Docker y solo consume la API publicada en loopback. |
| **Backend con usuario no root** | Reduce el impacto de una eventual ejecución de código no confiable dentro del contenedor. |
| **n8n: imagen fijada y volumen propio** | Se fija una versión estable explícita, se publica solo en `127.0.0.1:5678` y se usa el volumen `n8n_data` para su SQLite interno. Sin conexión a PostgreSQL. |
| **Redes Docker separadas** | PostgreSQL usa `postgres_net`, n8n usa `n8n_net` y Ollama usa `ai_net`. El backend es el único servicio presente en las tres. |
| **n8n: bloqueo de variables de entorno en nodos** | `N8N_BLOCK_ENV_ACCESS_IN_NODE=true` evita que expresiones y nodos Code lean variables del contenedor, incluida la clave de cifrado. |
| **IA local: Ollama en Docker** | Permite usar Ollama sin publicar el puerto `11434` en Windows, sin depender de `host.docker.internal` y sin modificar el firewall. |
| **Modelo inicial: qwen2.5:3b-instruct** | Equilibrio razonable entre tamaño, rendimiento en CPU/GPU modesta y capacidad para extracción/JSON. Configurable. |
| **Proveedor IA configurable (interfaz, previsto para la Fase 5)** | Permitirá cambiar modelo/proveedor sin reescribir la lógica de negocio. |
| **Docker Compose** | Orquestación local reproducible. |
| **Migraciones: Alembic** | Versionado de esquema PostgreSQL. La vía principal es el contenedor del backend; desde Windows se puede usar una sobrescritura temporal de `DATABASE_URL` con host `127.0.0.1`, sin modificar `.env`. |
| **Concurrencia de ejecuciones: `SELECT ... FOR UPDATE`** | Serializa las transiciones por fila en PostgreSQL y evita carreras entre estados y auditoría. |
| **Restricción `CHECK` de estados** | La base de datos solo admite `pending`, `running`, `completed`, `failed` y `cancelled`. |
| **Pruebas backend: pytest** | Estándar en Python. Las pruebas unitarias no requieren servicios externos. |
| **Pruebas de concurrencia: PostgreSQL con Testcontainers** | Usan un contenedor efímero aislado; no reutilizan la base local ni sus volúmenes. El puerto se publica solo en `127.0.0.1` con asignación aleatoria de Docker. |
| **Pruebas API: Postman** | Documentación y pruebas manuales/automatizables. |
| **Control de versiones: Git + GitHub** | Trazabilidad, ramas, PRs. |
| **Idioma español** | Toda documentación dirigida a personas en español. Código en inglés por convención. |
| **Backend como frontera** | Frontend NO accede directo a DB/Ollama/n8n. Solo vía API backend. |
| **CORS restringido** | FastAPI permite únicamente los orígenes locales configurados para Angular. |
| **Validación estricta salidas IA** | Usar esquemas/Pydantic, rechazar respuestas malformadas, registrar errores. |
| **Local-first sin claves pago** | Objetivo del portfolio. |
| **Ramas y PRs** | Nunca trabajar en main, usar feat/fix/docs/test/chore, PR hacia main sin merge automático. |
| **AGENTS.md versionado** | Instrucciones persistentes para agentes, visibles en repo. |

## Notas

- FastAPI, PostgreSQL, n8n y Ollama se ejecutan en Docker Desktop sobre Windows.
- Angular se ejecutará en Windows y solo accederá a FastAPI en `http://localhost:8000`.
- Las direcciones entre servicios se configuran explícitamente con nombres DNS de Compose.
- Sin secretos en código/versionado.
- `N8N_ENCRYPTION_KEY` se obtiene de `.env`, no tiene valor por defecto y debe conservarse mientras exista el volumen `n8n_data`.
- n8n usa HTTP local con `N8N_SECURE_COOKIE=false`; esta configuración es solo para desarrollo en `127.0.0.1`.
- n8n y PostgreSQL usan redes Docker exclusivas. El backend está en ambas para poder comunicarse con los dos.
- La comunicación n8n -> FastAPI usará `http://backend:8000`; la comunicación FastAPI -> n8n usará `http://n8n:5678`. No se necesita `host.docker.internal`.
- Ollama solo comparte la red `ai_net` con el backend y no publica puertos en Windows.
- Las redes no se configuran como `internal: true`; se mantienen como redes bridge locales para preservar el acceso desde el host y permitir la descarga de imágenes y modelos.
- Los puertos publicados se enlazan exclusivamente a `127.0.0.1`.
- `DATABASE_URL` dentro de Docker apunta a `postgres:5432`; `POSTGRES_HOST` y `POSTGRES_PORT` quedan para herramientas lanzadas desde Windows. Para ejecutar Alembic desde Windows se sobrescribe `DATABASE_URL` únicamente en la sesión de PowerShell, sin editar `.env`.
- Con la implementación actual, `POSTGRES_PASSWORD` debe usar solo caracteres URL-safe: letras ASCII, dígitos, guion bajo (`_`) y guion (`-`). Compose interpola la contraseña directamente en `DATABASE_URL`; los caracteres reservados pueden alterar la URL. No es una limitación inherente a PostgreSQL. Si se necesitan contraseñas arbitrarias, se deberá construir la URL con `sqlalchemy.engine.URL.create()` a partir de componentes separados, pasando la contraseña original sin percent-encoding manual.
- Las transiciones de `Execution` se serializan con bloqueo pesimista por fila. SQLite se usa para pruebas de lógica y atomicidad, no como evidencia de concurrencia real.
- Las pruebas de concurrencia requieren Docker y Testcontainers. Si falta Testcontainers, la importación falla de forma visible; si Docker no está disponible, el preflight omite explícitamente las pruebas en lugar de simular un resultado.
- El contenedor PostgreSQL efímero de pruebas se publica únicamente en `127.0.0.1` y utiliza un puerto libre asignado por Docker.
- No se ha comprobado la compatibilidad de GPU con Docker Desktop/WSL2. Ollama se ejecutará en CPU hasta validar esa compatibilidad.
- No se ha descargado ningún modelo de Ollama en esta fase.
