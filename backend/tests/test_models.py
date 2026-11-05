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


def test_execution_create_schema_ignores_managed_fields():
    data = {
        "status": "completed",
        "started_at": "2000-01-01T00:00:00Z",
        "finished_at": "2000-01-01T01:00:00Z",
        "trigger_source": "api",
    }
    schema = ExecutionCreate(**data)

    assert schema.trigger_source == "api"
    assert not hasattr(schema, "status")
    assert not hasattr(schema, "started_at")
    assert not hasattr(schema, "finished_at")
    assert "status" not in schema.model_dump()
    assert "started_at" not in schema.model_dump()
    assert "finished_at" not in schema.model_dump()


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
    assert schema.trigger_source == "api"
    assert schema.metadata == {}
