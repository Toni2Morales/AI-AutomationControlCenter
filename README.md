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
- Python 3.12 (objetivo). Se utilizará con un entorno virtual propio para el backend. Actualmente puede no estar instalado.
- Ollama instalado y accesible en http://localhost:11434
- Espacio suficiente en disco

## Estructura del repositorio

`
AI-AutomationControlCenter/
├── frontend/      # Aplicación Angular (pendiente)
├── backend/       # API FastAPI (pendiente)
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
`

## Cómo se iniciará la aplicación (previsto)

1. Copiar .env.example a .env y configurar los valores locales.
2. Crear y activar un entorno virtual con Python 3.12 para ackend/.
3. Levantar los servicios con Docker Compose cuando esté disponible.
4. Ejecutar migraciones con Alembic.
5. Iniciar backend y frontend según la documentación.

> En la fase actual no hay código ejecutable ni docker-compose.yml definitivo.

## Estado real del desarrollo

- [x] Estructura de carpetas creada
- [x] Documentación base en español
- [x] Plantilla .env.example
- [x] .gitignore configurado
- [x] AGENTS.md versionado
- [ ] Backend implementado
- [ ] Frontend implementado
- [ ] Infraestructura Docker Compose
- [ ] Flujos n8n
- [ ] Pruebas, migraciones y evaluación

## Licencia

Ver archivo LICENSE.
