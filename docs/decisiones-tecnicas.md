# Decisiones técnicas

## Decisiones confirmadas

| Decisión | Motivo |
|---|---|
| **Frontend: Angular + TypeScript en modo estricto** | Estructura sólida, tipado fuerte, buen para portfolio profesional. |
| **Backend: FastAPI (Python)** | Rápido para APIs REST, validación con Pydantic, documentación automática, ideal para integrar IA. |
| **Python 3.12 (objetivo)** | Versión estable objetivo. Usar entorno virtual propio. Si no está instalado, documentar requisito sin instalar globalmente. |
| **Base de datos: PostgreSQL** | Robusto, relacional, ampliamente usado, buen para trazabilidad/auditoría. |
| **Automatización: n8n autoalojado** | Permite orquestar flujos localmente, exportar flujos como JSON versionados. |
| **IA local: Ollama** | Funciona 100% local, sin claves de pago para funcionalidad principal. |
| **Modelo inicial: qwen2.5:3b-instruct** | Equilibrio razonable entre tamaño, rendimiento en CPU/GPU modesta (GTX 960) y capacidad para extracción/JSON. Configurable. |
| **Proveedor IA configurable (interfaz)** | Permite cambiar modelo/proveedor sin reescribir lógica de negocio. |
| **Docker Compose** | Orquestación local reproducible. |
| **Migraciones: Alembic** | Versionado de esquema PostgreSQL. |
| **Pruebas backend: pytest** | Estándar en Python. |
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
