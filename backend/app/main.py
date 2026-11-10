from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes
from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title="AI Automation Control Center",
    description="API REST local para automatización, evaluación de prompts y trazabilidad.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Accept", "Content-Type", "Authorization", "X-Integration-Token"],
)

app.include_router(routes.router)
app.include_router(api_router, prefix="/api/v1")
