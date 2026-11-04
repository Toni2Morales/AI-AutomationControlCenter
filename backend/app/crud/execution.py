"""CRUD para ejecuciones."""

from sqlalchemy.orm import Session

from app.models.execution import Execution
from app.schemas.execution import ExecutionCreate


def create_execution(db: Session, execution_in: ExecutionCreate) -> Execution:
    """Crear una nueva ejecución.

    Los valores por defecto del modelo se aplican si no se especifican.
    """
    execution_data = execution_in.model_dump()
    # Mapear metadata a extra_metadata para el modelo ORM
    if "metadata" in execution_data:
        execution_data["extra_metadata"] = execution_data.pop("metadata")
    db_execution = Execution(**execution_data)
    try:
        db.add(db_execution)
        db.commit()
        db.refresh(db_execution)
        return db_execution
    except Exception:
        db.rollback()
        raise


def get_executions(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    trigger_source: str | None = None,
) -> tuple[list[Execution], int]:
    """Obtener ejecuciones paginadas con filtros opcionales."""
    query = db.query(Execution)

    if status is not None:
        query = query.filter(Execution.status == status)
    if trigger_source is not None:
        query = query.filter(Execution.trigger_source == trigger_source)

    total = query.count()

    offset = (page - 1) * page_size
    items = (
        query.order_by(Execution.created_at.desc(), Execution.id.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )
    return items, total


def get_execution(db: Session, execution_id: int) -> Execution | None:
    """Obtener una ejecución por ID."""
    return db.query(Execution).filter(Execution.id == execution_id).first()


class InvalidExecutionTransitionError(Exception):
    """Excepción para transiciones de estado inválidas."""


ALLOWED_TRANSITIONS = {
    "pending": {"running", "cancelled"},
    "running": {"completed", "failed", "cancelled"},
}


def update_execution_status(db: Session, execution_id: int, new_status: str) -> Execution | None:
    """Actualizar el estado de una ejecución siguiendo las transiciones permitidas."""
    from datetime import UTC, datetime

    db_execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if db_execution is None:
        return None

    current_status = db_execution.status
    if current_status in {"completed", "failed", "cancelled"}:
        raise InvalidExecutionTransitionError(
            "No se puede modificar una ejecución en estado terminal"
        )

    allowed = ALLOWED_TRANSITIONS.get(current_status, set())
    if new_status not in allowed:
        raise InvalidExecutionTransitionError("Transición de estado no permitida")

    db_execution.status = new_status
    if new_status == "running" and db_execution.started_at is None:
        db_execution.started_at = datetime.now(UTC)
    if new_status in {"completed", "failed", "cancelled"}:
        db_execution.finished_at = datetime.now(UTC)

    try:
        db.commit()
        db.refresh(db_execution)
        return db_execution
    except Exception:
        db.rollback()
        raise


def get_audit_logs_by_execution(db: Session, execution_id: int):
    """Obtener registros de auditoría de una ejecución."""
    from app.models.audit_log import AuditLog

    return (
        db.query(AuditLog)
        .filter(AuditLog.execution_id == execution_id)
        .order_by(AuditLog.created_at.asc(), AuditLog.id.asc())
        .all()
    )
