from fastapi import FastAPI

from app.api import routes

app = FastAPI(
    title="AI Automation Control Center",
    description="API REST local para automatización, evaluación de prompts y trazabilidad.",
)

app.include_router(routes.router)
