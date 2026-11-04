from fastapi import FastAPI

from app.api import routes
from app.api.v1.router import api_router

app = FastAPI(
    title="AI Automation Control Center",
    description="API REST local para automatización, evaluación de prompts y trazabilidad.",
)

app.include_router(routes.router)
app.include_router(api_router, prefix="/api/v1")
