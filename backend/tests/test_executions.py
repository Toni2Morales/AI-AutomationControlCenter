from datetime import UTC, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.endpoints.executions import _as_utc
from app.core.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def setup_module():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db


def teardown_module():
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def setup_function():
    db = TestingSessionLocal()
    try:
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()
    finally:
        db.close()


client = TestClient(app)


def _create_execution(payload: dict | None = None) -> dict:
    """Crear una ejecución por API y devolver su representación pública."""
    response = client.post("/api/v1/executions/", json=payload or {})
    assert response.status_code == 201
    return response.json()


def _get_audit_logs(execution_id: int) -> list[dict]:
    """Obtener los registros de auditoría de una ejecución."""
    response = client.get(f"/api/v1/executions/{execution_id}/audit-logs")
    assert response.status_code == 200
    return response.json()


def test_as_utc_treats_naive_datetimes_as_utc():
    naive = datetime(2026, 1, 2, 3, 4, 5)

    normalized = _as_utc(naive)

    assert normalized == naive.replace(tzinfo=UTC)
    assert normalized is not None
    assert normalized.utcoffset() == timedelta(0)


def test_as_utc_converts_aware_datetimes_to_utc():
    source = datetime(2026, 1, 2, 3, 4, 5, tzinfo=timezone(timedelta(hours=2)))

    normalized = _as_utc(source)

    assert normalized == datetime(2026, 1, 2, 1, 4, 5, tzinfo=UTC)
    assert normalized is not None
    assert normalized.utcoffset() == timedelta(0)


def test_create_execution_minimal():
    response = client.post("/api/v1/executions/", json={})
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert isinstance(data["id"], int)
    assert "created_at" in data
    assert "updated_at" in data


def test_create_execution_with_trigger_and_metadata():
    payload = {"trigger_source": "manual", "metadata": {"foo": "bar"}}
    response = client.post("/api/v1/executions/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["trigger_source"] == "manual"
    assert data["metadata"] == {"foo": "bar"}


def test_create_execution_ignores_managed_fields():
    payload = {
        "id": 999,
        "created_at": "2000-01-01T00:00:00Z",
        "updated_at": "2000-01-01T00:00:00Z",
        "status": "completed",
        "started_at": "2000-01-01T00:00:00Z",
        "finished_at": "2000-01-01T01:00:00Z",
    }
    response = client.post("/api/v1/executions/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] != 999
    assert data["status"] == "pending"
    assert data["started_at"] is None
    assert data["finished_at"] is None


def test_create_execution_persisted():
    response = client.post("/api/v1/executions/", json={"trigger_source": "test"})
    assert response.status_code == 201
    data = response.json()
    execution_id = data["id"]
    db = TestingSessionLocal()
    try:
        from app.models.execution import Execution

        obj = db.query(Execution).filter(Execution.id == execution_id).first()
        assert obj is not None
        assert obj.status == "pending"
        assert obj.started_at is None
        assert obj.finished_at is None
        assert obj.trigger_source == "test"
    finally:
        db.close()


def test_create_execution_registers_audit_log():
    data = _create_execution({"trigger_source": "manual"})
    logs = _get_audit_logs(data["id"])

    assert len(logs) == 1
    log = logs[0]
    assert log["execution_id"] == data["id"]
    assert log["event_type"] == "execution.created"
    assert log["message"]
    assert log["details"] == {"status": "pending", "trigger_source": "manual"}
    assert log["created_at"] is not None


def test_create_execution_rolls_back_if_audit_fails(monkeypatch):
    from app.crud import execution as execution_crud
    from app.models.audit_log import AuditLog
    from app.models.execution import Execution
    from app.schemas.execution import ExecutionCreate

    def failing_audit_log(*args, **kwargs):
        raise RuntimeError("fallo simulado al registrar auditoría")

    monkeypatch.setattr(execution_crud, "AuditLog", failing_audit_log)

    db = TestingSessionLocal()
    try:
        with pytest.raises(RuntimeError):
            execution_crud.create_execution(db, ExecutionCreate(trigger_source="test"))
    finally:
        db.close()

    db = TestingSessionLocal()
    try:
        assert db.query(Execution).count() == 0
        assert db.query(AuditLog).count() == 0
    finally:
        db.close()


def test_list_executions_empty():
    response = client.get("/api/v1/executions/")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["page_size"] == 20


def test_list_executions_with_items():
    client.post(
        "/api/v1/executions/", json={"trigger_source": "a", "metadata": {"k": "v"}}
    )
    client.post("/api/v1/executions/", json={"trigger_source": "b"})
    response = client.get("/api/v1/executions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 2
    by_source = {item["trigger_source"]: item for item in data["items"]}
    assert by_source["a"]["metadata"] == {"k": "v"}
    assert by_source["b"]["metadata"] is None


def test_list_executions_pagination():
    for i in range(5):
        client.post("/api/v1/executions/", json={"trigger_source": str(i)})
    response = client.get("/api/v1/executions/?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 2

    response2 = client.get("/api/v1/executions/?page=3&page_size=2")
    assert response2.status_code == 200
    data2 = response2.json()
    assert len(data2["items"]) == 1


def test_list_executions_order_desc():
    client.post("/api/v1/executions/", json={"trigger_source": "first"})
    client.post("/api/v1/executions/", json={"trigger_source": "second"})
    response = client.get("/api/v1/executions/")
    data = response.json()
    items = data["items"]
    assert items[0]["trigger_source"] == "second"
    assert items[1]["trigger_source"] == "first"
    assert items[0]["id"] > items[1]["id"]


def test_list_executions_filter_status():
    client.post("/api/v1/executions/", json={"trigger_source": "x"})
    response = client.get("/api/v1/executions/?status=pending")
    assert response.status_code == 200
    assert response.json()["total"] >= 1
    response2 = client.get("/api/v1/executions/?status=completed")
    assert response2.status_code == 200
    assert response2.json()["total"] == 0


def test_list_executions_filter_trigger_source():
    client.post("/api/v1/executions/", json={"trigger_source": "manual"})
    client.post("/api/v1/executions/", json={"trigger_source": "n8n"})
    response = client.get("/api/v1/executions/?trigger_source=manual")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    for item in data["items"]:
        assert item["trigger_source"] == "manual"


def test_list_executions_combined_filters():
    client.post("/api/v1/executions/", json={"trigger_source": "manual"})
    response = client.get("/api/v1/executions/?status=pending&trigger_source=manual")
    assert response.status_code == 200
    assert response.json()["total"] >= 1


def test_list_executions_total_with_pagination():
    for _ in range(10):
        client.post("/api/v1/executions/", json={})
    response = client.get("/api/v1/executions/?page=2&page_size=3")
    data = response.json()
    assert data["total"] == 10
    assert len(data["items"]) == 3


def test_list_executions_page_zero_422():
    response = client.get("/api/v1/executions/?page=0")
    assert response.status_code == 422


def test_list_executions_page_size_too_large_422():
    response = client.get("/api/v1/executions/?page_size=101")
    assert response.status_code == 422


def test_list_executions_invalid_status_422():
    response = client.get("/api/v1/executions/?status=invalid_status")
    assert response.status_code == 422


def test_get_execution_success():
    response = client.post("/api/v1/executions/", json={"trigger_source": "test"})
    assert response.status_code == 201
    data = response.json()
    execution_id = data["id"]
    response2 = client.get(f"/api/v1/executions/{execution_id}")
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["id"] == execution_id
    assert data2["status"] == "pending"


def test_get_execution_not_found():
    response = client.get("/api/v1/executions/999999")
    assert response.status_code == 404


def test_get_execution_invalid_id():
    response = client.get("/api/v1/executions/abc")
    assert response.status_code == 422


def test_get_execution_with_metadata():
    response = client.post(
        "/api/v1/executions/", json={"trigger_source": "x", "metadata": {"key": "value"}}
    )
    assert response.status_code == 201
    data = response.json()
    execution_id = data["id"]
    response2 = client.get(f"/api/v1/executions/{execution_id}")
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["metadata"] == {"key": "value"}


def test_patch_pending_to_running():
    response = client.post("/api/v1/executions/", json={})
    execution_id = response.json()["id"]
    response2 = client.patch(
        f"/api/v1/executions/{execution_id}/status", json={"status": "running"}
    )
    assert response2.status_code == 200
    data = response2.json()
    assert data["status"] == "running"
    assert data["started_at"] is not None


def test_patch_running_to_completed():
    response = client.post("/api/v1/executions/", json={})
    execution_id = response.json()["id"]
    client.patch(f"/api/v1/executions/{execution_id}/status", json={"status": "running"})
    response2 = client.patch(
        f"/api/v1/executions/{execution_id}/status", json={"status": "completed"}
    )
    assert response2.status_code == 200
    data = response2.json()
    assert data["status"] == "completed"
    assert data["finished_at"] is not None


def test_patch_running_to_failed():
    response = client.post("/api/v1/executions/", json={})
    execution_id = response.json()["id"]
    client.patch(f"/api/v1/executions/{execution_id}/status", json={"status": "running"})
    response2 = client.patch(
        f"/api/v1/executions/{execution_id}/status", json={"status": "failed"}
    )
    assert response2.status_code == 200
    assert response2.json()["status"] == "failed"
    assert response2.json()["finished_at"] is not None


def test_patch_pending_to_cancelled():
    response = client.post("/api/v1/executions/", json={})
    execution_id = response.json()["id"]
    response2 = client.patch(
        f"/api/v1/executions/{execution_id}/status", json={"status": "cancelled"}
    )
    assert response2.status_code == 200
    data = response2.json()
    assert data["status"] == "cancelled"
    assert data["finished_at"] is not None


def test_patch_running_to_cancelled():
    response = client.post("/api/v1/executions/", json={})
    execution_id = response.json()["id"]
    client.patch(f"/api/v1/executions/{execution_id}/status", json={"status": "running"})
    response2 = client.patch(
        f"/api/v1/executions/{execution_id}/status", json={"status": "cancelled"}
    )
    assert response2.status_code == 200
    assert response2.json()["status"] == "cancelled"


def test_patch_invalid_pending_to_completed():
    response = client.post("/api/v1/executions/", json={})
    execution_id = response.json()["id"]
    response2 = client.patch(
        f"/api/v1/executions/{execution_id}/status", json={"status": "completed"}
    )
    assert response2.status_code == 422


def test_patch_invalid_completed_to_running():
    response = client.post("/api/v1/executions/", json={})
    execution_id = response.json()["id"]
    client.patch(f"/api/v1/executions/{execution_id}/status", json={"status": "running"})
    client.patch(f"/api/v1/executions/{execution_id}/status", json={"status": "completed"})
    response2 = client.patch(
        f"/api/v1/executions/{execution_id}/status", json={"status": "running"}
    )
    assert response2.status_code == 422


def test_patch_invalid_failed_to_completed():
    response = client.post("/api/v1/executions/", json={})
    execution_id = response.json()["id"]
    client.patch(f"/api/v1/executions/{execution_id}/status", json={"status": "running"})
    client.patch(f"/api/v1/executions/{execution_id}/status", json={"status": "failed"})
    response2 = client.patch(
        f"/api/v1/executions/{execution_id}/status", json={"status": "completed"}
    )
    assert response2.status_code == 422


def test_patch_invalid_cancelled_to_running():
    response = client.post("/api/v1/executions/", json={})
    execution_id = response.json()["id"]
    client.patch(f"/api/v1/executions/{execution_id}/status", json={"status": "cancelled"})
    response2 = client.patch(
        f"/api/v1/executions/{execution_id}/status", json={"status": "running"}
    )
    assert response2.status_code == 422


def test_patch_not_found():
    response = client.patch("/api/v1/executions/999999/status", json={"status": "running"})
    assert response.status_code == 404


def test_patch_invalid_id():
    response = client.patch("/api/v1/executions/abc/status", json={"status": "running"})
    assert response.status_code == 422


def test_patch_rejects_unknown_status():
    execution = _create_execution()
    response = client.patch(
        f"/api/v1/executions/{execution['id']}/status", json={"status": "unknown"}
    )
    assert response.status_code == 422


def test_database_rejects_invalid_status():
    from sqlalchemy.exc import IntegrityError

    from app.models.execution import Execution

    db = TestingSessionLocal()
    try:
        db.add(Execution(status="invalid"))
        with pytest.raises(IntegrityError):
            db.commit()
    finally:
        db.rollback()
        db.close()


def test_patch_cannot_set_started_at():
    response = client.post("/api/v1/executions/", json={})
    execution_id = response.json()["id"]
    response2 = client.patch(
        f"/api/v1/executions/{execution_id}/status",
        json={"status": "running", "started_at": "2000-01-01T00:00:00Z"},
    )
    assert response2.status_code == 200
    data = response2.json()
    assert data["started_at"] is not None
    assert "2000" not in str(data["started_at"])


def test_patch_cannot_set_finished_at():
    response = client.post("/api/v1/executions/", json={})
    execution_id = response.json()["id"]
    response2 = client.patch(
        f"/api/v1/executions/{execution_id}/status",
        json={"status": "cancelled", "finished_at": "2000-01-01T00:00:00Z"},
    )
    assert response2.status_code == 200
    data = response2.json()
    assert data["finished_at"] is not None
    assert "2000" not in str(data["finished_at"])


def test_patch_metadata_preserved():
    response = client.post("/api/v1/executions/", json={"metadata": {"a": 1}})
    execution_id = response.json()["id"]
    response2 = client.patch(
        f"/api/v1/executions/{execution_id}/status", json={"status": "running"}
    )
    assert response2.status_code == 200
    assert response2.json()["metadata"] == {"a": 1}


TRANSITION_EVENTS = {
    "running": "execution.started",
    "completed": "execution.completed",
    "failed": "execution.failed",
    "cancelled": "execution.cancelled",
}


@pytest.mark.parametrize(
    ("steps", "expected_previous", "expected_new"),
    [
        (("running",), "pending", "running"),
        (("running", "completed"), "running", "completed"),
        (("running", "failed"), "running", "failed"),
        (("cancelled",), "pending", "cancelled"),
        (("running", "cancelled"), "running", "cancelled"),
    ],
)
def test_valid_transition_registers_audit_log(steps, expected_previous, expected_new):
    execution = _create_execution()
    for step in steps:
        response = client.patch(
            f"/api/v1/executions/{execution['id']}/status", json={"status": step}
        )
        assert response.status_code == 200

    logs = _get_audit_logs(execution["id"])
    expected_events = [
        "execution.created",
        *[TRANSITION_EVENTS[step] for step in steps],
    ]
    assert [log["event_type"] for log in logs] == expected_events

    last_log = logs[-1]
    assert last_log["message"]
    assert last_log["details"] == {
        "previous_status": expected_previous,
        "new_status": expected_new,
    }


def test_invalid_transition_does_not_register_audit_log():
    execution = _create_execution()
    response = client.patch(
        f"/api/v1/executions/{execution['id']}/status", json={"status": "completed"}
    )
    assert response.status_code == 422

    logs = _get_audit_logs(execution["id"])
    assert [log["event_type"] for log in logs] == ["execution.created"]


def test_invalid_transition_does_not_change_execution():
    execution = _create_execution()
    response = client.patch(
        f"/api/v1/executions/{execution['id']}/status", json={"status": "completed"}
    )
    assert response.status_code == 422

    response2 = client.get(f"/api/v1/executions/{execution['id']}")
    assert response2.status_code == 200
    data = response2.json()
    assert data["status"] == "pending"
    assert data["started_at"] is None
    assert data["finished_at"] is None


def test_invalid_terminal_transition_does_not_register_audit_log():
    execution = _create_execution()
    execution_id = execution["id"]
    client.patch(f"/api/v1/executions/{execution_id}/status", json={"status": "running"})
    client.patch(f"/api/v1/executions/{execution_id}/status", json={"status": "completed"})
    logs_before = _get_audit_logs(execution_id)

    response = client.patch(
        f"/api/v1/executions/{execution_id}/status", json={"status": "running"}
    )
    assert response.status_code == 422
    assert _get_audit_logs(execution_id) == logs_before


def test_idempotent_transition_does_not_duplicate_audit_log():
    execution = _create_execution()
    execution_id = execution["id"]
    first = client.patch(
        f"/api/v1/executions/{execution_id}/status", json={"status": "running"}
    )
    assert first.status_code == 200
    logs_after_start = _get_audit_logs(execution_id)

    repeated = client.patch(
        f"/api/v1/executions/{execution_id}/status", json={"status": "running"}
    )
    assert repeated.status_code == 200
    assert repeated.json()["started_at"] == first.json()["started_at"]
    assert _get_audit_logs(execution_id) == logs_after_start

    client.patch(f"/api/v1/executions/{execution_id}/status", json={"status": "completed"})
    logs_after_completion = _get_audit_logs(execution_id)
    repeated_terminal = client.patch(
        f"/api/v1/executions/{execution_id}/status", json={"status": "completed"}
    )
    assert repeated_terminal.status_code == 200
    assert _get_audit_logs(execution_id) == logs_after_completion


def test_transition_rolls_back_if_audit_fails(monkeypatch):
    from app.crud import execution as execution_crud

    execution = _create_execution()
    execution_id = execution["id"]
    logs_before = _get_audit_logs(execution_id)

    def failing_audit_log(*args, **kwargs):
        raise RuntimeError("fallo simulado al registrar auditoría")

    monkeypatch.setattr(execution_crud, "AuditLog", failing_audit_log)

    db = TestingSessionLocal()
    try:
        with pytest.raises(RuntimeError):
            execution_crud.update_execution_status(db, execution_id, "running")
    finally:
        db.close()

    monkeypatch.undo()

    response = client.get(f"/api/v1/executions/{execution_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert data["started_at"] is None
    assert data["finished_at"] is None
    assert _get_audit_logs(execution_id) == logs_before


def test_get_audit_logs_after_creation():
    execution = _create_execution()
    logs = _get_audit_logs(execution["id"])
    assert len(logs) == 1
    assert logs[0]["event_type"] == "execution.created"


def test_get_audit_logs_with_items_order():
    from app.models.audit_log import AuditLog

    execution = _create_execution()
    execution_id = execution["id"]
    db = TestingSessionLocal()
    try:
        db.add(AuditLog(execution_id=execution_id, event_type="start", message="inicio"))
        db.add(AuditLog(execution_id=execution_id, event_type="end", message="fin"))
        db.commit()
    finally:
        db.close()
    logs = _get_audit_logs(execution_id)
    assert len(logs) == 3
    assert [log["event_type"] for log in logs] == ["execution.created", "start", "end"]
    for previous, current in zip(logs, logs[1:], strict=False):
        assert previous["created_at"] <= current["created_at"]


def test_get_audit_logs_not_found():
    response = client.get("/api/v1/executions/999999/audit-logs")
    assert response.status_code == 404


def test_get_audit_logs_invalid_id():
    response = client.get("/api/v1/executions/abc/audit-logs")
    assert response.status_code == 422


def test_get_audit_logs_isolation():
    from app.models.audit_log import AuditLog

    r1 = client.post("/api/v1/executions/", json={})
    r2 = client.post("/api/v1/executions/", json={})
    id1 = r1.json()["id"]
    id2 = r2.json()["id"]
    db = TestingSessionLocal()
    try:
        db.add(AuditLog(execution_id=id1, event_type="a", message="m1"))
        db.add(AuditLog(execution_id=id2, event_type="b", message="m2"))
        db.commit()
    finally:
        db.close()
    resp1 = client.get(f"/api/v1/executions/{id1}/audit-logs")
    resp2 = client.get(f"/api/v1/executions/{id2}/audit-logs")
    assert resp1.status_code == 200
    assert resp2.status_code == 200
    assert len(resp1.json()) == 2
    assert len(resp2.json()) == 2
    assert resp1.json()[0]["event_type"] == "execution.created"
    assert resp2.json()[0]["event_type"] == "execution.created"
    assert resp1.json()[1]["message"] == "m1"
    assert resp2.json()[1]["message"] == "m2"


def test_openapi_has_executions_endpoints():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    paths = data.get("paths", {})
    assert "/api/v1/executions/" in paths
    assert "/api/v1/executions/{execution_id}" in paths
    assert "/api/v1/executions/{execution_id}/status" in paths
    assert "/api/v1/executions/{execution_id}/audit-logs" in paths


def test_openapi_page_schema_exists():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    schemas = data.get("components", {}).get("schemas", {})
    assert "Page_ExecutionRead_" in schemas or any("Page" in k for k in schemas)


def test_openapi_audit_log_schema_exists():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    schemas = data.get("components", {}).get("schemas", {})
    assert "AuditLogRead" in schemas
