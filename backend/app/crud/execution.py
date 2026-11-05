"""CRUD para ejecuciones."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.execution import Execution
from app.schemas.execution import ExecutionCreate

TERMINAL_STATUSES = {"completed", "failed", "cancelled"}

TRANSITION_EVENTS = {
    "running": "execution.started",
    "completed": "execution.completed",
    "failed": "execution.failed",
    "cancelled": "execution.cancelled",
}

TRANSITION_MESSAGES = {
    "running": "Ejecución iniciada",
    "completed": "Ejecución completada",
    "failed": "Ejecución fallida",
    "cancelled": "Ejecución cancelada",
}


def create_execution(db: Session, execution_in: ExecutionCreate) -> Execution:
    """Crear una nueva ejecución en estado ``pending``.

    El estado y los timestamps siempre los fija el servidor. La creación y su
    registro de auditoría se confirman en la misma transacción.
    """
    execution_data = execution_in.model_dump()
    # Mapear metadata a extra_metadata para el modelo ORM
    if "metadata" in execution_data:
        execution_data["extra_metadata"] = execution_data.pop("metadata")

    db_execution = Execution(
        **execution_data,
        status="pending",
        started_at=None,
        finished_at=None,
    )
    try:
        db.add(db_execution)
        # Necesario para disponer del ID antes de crear el registro de auditoría.
        db.flush()
        db.add(
            AuditLog(
                execution_id=db_execution.id,
                event_type="execution.created",
                message="Ejecución creada en estado pendiente",
                details={
                    "status": db_execution.status,
                    "trigger_source": db_execution.trigger_source,
                },
            )
        )
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
    """Actualizar el estado de una ejecución siguiendo las transiciones permitidas.

    Si el estado solicitado coincide con el actual, la operación es idempotente:
    no se modifica nada ni se genera un nuevo registro de auditoría.
    """
    db_execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if db_execution is None:
        return None

    current_status = db_execution.status
    if new_status == current_status:
        return db_execution

    if current_status in TERMINAL_STATUSES:
        raise InvalidExecutionTransitionError(
            "No se puede modificar una ejecución en estado terminal"
        )

    allowed = ALLOWED_TRANSITIONS.get(current_status, set())
    if new_status not in allowed:
        raise InvalidExecutionTransitionError("Transición de estado no permitida")

    try:
        now = datetime.now(UTC)
        db_execution.status = new_status
        if new_status == "running":
            db_execution.started_at = now
        if new_status in TERMINAL_STATUSES:
            db_execution.finished_at = now

        db.add(
            AuditLog(
                execution_id=db_execution.id,
                event_type=TRANSITION_EVENTS[new_status],
                message=TRANSITION_MESSAGES[new_status],
                details={
                    "previous_status": current_status,
                    "new_status": new_status,
                },
            )
        )

        db.commit()
        db.refresh(db_execution)
        return db_execution
    except Exception:
        db.rollback()
        raise


def get_audit_logs_by_execution(db: Session, execution_id: int) -> list[AuditLog]:
    """Obtener registros de auditoría de una ejecución."""
    return (
        db.query(AuditLog)
        .filter(AuditLog.execution_id == execution_id)
        .order_by(AuditLog.created_at.asc(), AuditLog.id.asc())
        .all()
    )
