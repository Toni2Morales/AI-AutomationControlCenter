# Arquitectura

## Visión general
AI Automation Control Center es una aplicación **local-first**. Todos los componentes se ejecutan en el entorno local. El frontend **únicamente** se comunica con el backend. El backend actúa como frontera única: es el único componente que accede a PostgreSQL, n8n y Ollama.

## Componentes y responsabilidades

| Componente | Tecnología | Responsabilidad | Acceso |
|---|---|---|---|
| **Frontend** | Angular + TypeScript (modo estricto) | Interfaz de usuario para subir archivos, consultar ejecuciones, ver resultados y auditoría. | Solo HTTP REST hacia el backend. |
| **Backend** | FastAPI (Python 3.12) | Lógica de negocio, validación, orquestación, interfaz de proveedor de IA configurable, gestión de auditoría y punto único de acceso. | Acceso a PostgreSQL, n8n y Ollama. Accesible únicamente de forma local. |
| **Base de datos** | PostgreSQL | Almacenamiento persistente, trazabilidad, auditoría y registros de ejecución. | **Solo** desde el backend. |
| **Automatización** | n8n autoalojado | Orquestación de flujos de trabajo. Puede ser invocado por el backend o invocar al backend según el flujo. | Local únicamente. Sin exposición pública. |
| **IA local** | Ollama | Inferencia local con modelos configurables. | **Solo** desde el backend mediante una interfaz de proveedor. |
| **Orquestación** | Docker Compose | Levantamiento local, red interna, volúmenes persistentes, orden de arranque y comprobaciones de salud. | Local. |

## Diagrama de comunicaciones (texto)

`
[Usuario] --> [Frontend Angular] --HTTP/JSON--> [Backend FastAPI]
                                                  |--SQL--> [PostgreSQL]
                                                  |--HTTP--> [n8n]
                                                  |--HTTP--> [Ollama]
`

**Límites de seguridad:**
- El frontend **no** accede directamente a PostgreSQL, Ollama ni n8n.
- PostgreSQL y n8n **no** se expondrán a redes públicas.
- Ollama se ejecuta localmente; la conexión se realiza desde el backend.
- Todos los puertos, cuando se expongan, se limitarán a 127.0.0.1.
- Las salidas del modelo de IA se validan contra esquemas explícitos.
- El modelo es configurable mediante variables de entorno a través de una interfaz de proveedor.
- Los secretos se gestionan con .env fuera de control de versiones.

## Principios arquitectónicos
- **Local-first:** Sin dependencia de servicios de pago para la funcionalidad principal.
- **Frontera única:** El backend es el punto de control.
- **Abstracción de IA:** Interfaz AIProvider con implementación OllamaProvider. Permite cambiar modelo sin modificar la lógica de negocio.
- **Validación estricta:** Respuestas del modelo validadas, errores controlados y registrados.
- **Trazabilidad y auditoría:** Registros de ejecución, errores y cambios relevantes.
- **Seguridad por defecto:** Sin credenciales en código, sin exposición pública, acceso restringido entre servicios.
- **Reproducible:** Entorno local documentado.

## Estado
**Previsto.** No existe código de implementación en esta fase.
