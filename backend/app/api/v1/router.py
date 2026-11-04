from fastapi import APIRouter

from app.api.v1.endpoints import executions

api_router = APIRouter()

api_router.include_router(executions.router, prefix="/executions", tags=["executions"])
