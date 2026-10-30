from datetime import UTC, datetime

from app.core.database import Base
from app.models import AuditLog, Execution
from app.schemas import AuditLogCreate, ExecutionCreate, ExecutionRead


def test_imports_models():
    assert Execution is not None
    assert AuditLog is not None


def test_tables_in_metadata():
    assert "executions" in Base.metadata.tables
    assert "audit_logs" in Base.metadata.tables


def test_execution_schema():
    data = {"status": "pending"}
    schema = ExecutionCreate(**data)
    assert schema.status == "pending"


def test_audit_log_schema():
    data = {"event_type": "test", "message": "hello"}
    schema = AuditLogCreate(**data)
    assert schema.event_type == "test"


def test_schema_from_attributes():
    class Dummy:
        pass

    d = Dummy()
    d.id = 1
    d.status = "completed"
    d.started_at = datetime.now(UTC)
    d.finished_at = datetime.now(UTC)
    d.error_message = None
    d.trigger_source = "api"
    d.metadata = {}
    d.created_at = datetime.now(UTC)
    d.updated_at = datetime.now(UTC)

    schema = ExecutionRead.model_validate(d)
    assert schema.id == 1
