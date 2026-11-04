from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import execution as execution_crud
from app.schemas.audit_log import AuditLogRead
from app.schemas.execution import ExecutionCreate, ExecutionRead
from app.schemas.pagination import Page

router = APIRouter()


class ExecutionStatusUpdate(BaseModel):
    """Cuerpo de petición para actualizar el estado de una ejecución."""
    status: Literal["running", "completed", "failed", "cancelled"]


def _execution_to_dict(item):
    """Convertir instancia ORM a dict compatible con ExecutionRead."""
    return {
        "status": item.status,
        "started_at": item.started_at,
        "finished_at": item.finished_at,
        "error_message": item.error_message,
        "trigger_source": item.trigger_source,
        "metadata": item.extra_metadata,
        "id": item.id,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


@router.post(
    "/",
    response_model=ExecutionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear ejecución",
    description="Crea una nueva ejecución. El estado inicial es 'pending'.",
)
def create_execution(execution_in: ExecutionCreate, db: Session = Depends(get_db)):
    """Crear una nueva ejecución."""
    item = execution_crud.create_execution(db=db, execution_in=execution_in)
    return _execution_to_dict(item)


@router.get(
    "/",
    response_model=Page[ExecutionRead],
    summary="Listar ejecuciones",
    description="Lista ejecuciones paginadas con filtros opcionales.",
)
def list_executions(
    page: int = Query(default=1, ge=1, description="Número de página (>=1)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Tamaño de página (1-100)"),
    status: Literal["pending", "running", "completed", "failed", "cancelled"] | None = Query(
        default=None, description="Filtrar por estado"
    ),
    trigger_source: str | None = Query(default=None, description="Filtrar por origen"),
    db: Session = Depends(get_db),
):
    """Listar ejecuciones paginadas."""
    items, total = execution_crud.get_executions(
        db=db,
        page=page,
        page_size=page_size,
        status=status,
        trigger_source=trigger_source,
    )
    result_items = [_execution_to_dict(item) for item in items]
    return Page[ExecutionRead](items=result_items, total=total, page=page, page_size=page_size)


@router.get(
    "/{execution_id}",
    response_model=ExecutionRead,
    summary="Obtener ejecución",
    description="Obtiene una ejecución por su ID.",
)
def get_execution(execution_id: int, db: Session = Depends(get_db)):
    """Obtener una ejecución por ID."""
    item = execution_crud.get_execution(db=db, execution_id=execution_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ejecución no encontrada")
    return _execution_to_dict(item)


@router.patch(
    "/{execution_id}/status",
    response_model=ExecutionRead,
    summary="Actualizar estado",
    description="Actualiza el estado siguiendo las transiciones permitidas.",
)
def update_execution_status(
    execution_id: int, update: ExecutionStatusUpdate, db: Session = Depends(get_db)
):
    """Actualizar el estado de una ejecución."""
    try:
        item = execution_crud.update_execution_status(
            db=db, execution_id=execution_id, new_status=update.status
        )
    except execution_crud.InvalidExecutionTransitionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ejecución no encontrada")
    return _execution_to_dict(item)


@router.get(
    "/{execution_id}/audit-logs",
    response_model=list[AuditLogRead],
    summary="Listar logs de auditoría",
    description="Lista los registros de auditoría de una ejecución ordenados por fecha.",
)
def get_execution_audit_logs(execution_id: int, db: Session = Depends(get_db)):
    """Consultar registros de auditoría de una ejecución."""
    item = execution_crud.get_execution(db=db, execution_id=execution_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ejecución no encontrada")
    logs = execution_crud.get_audit_logs_by_execution(db=db, execution_id=execution_id)
    return logs
