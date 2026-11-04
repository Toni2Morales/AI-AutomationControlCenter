from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

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
        "status": "pending",
    }
    response = client.post("/api/v1/executions/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] != 999


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
        assert obj.trigger_source == "test"
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


def test_get_audit_logs_empty():
    response = client.post("/api/v1/executions/", json={})
    execution_id = response.json()["id"]
    response2 = client.get(f"/api/v1/executions/{execution_id}/audit-logs")
    assert response2.status_code == 200
    assert response2.json() == []


def test_get_audit_logs_with_items_order():
    from app.models.audit_log import AuditLog

    response = client.post("/api/v1/executions/", json={})
    execution_id = response.json()["id"]
    db = TestingSessionLocal()
    try:
        db.add(AuditLog(execution_id=execution_id, event_type="start", message="inicio"))
        db.add(AuditLog(execution_id=execution_id, event_type="end", message="fin"))
        db.commit()
    finally:
        db.close()
    response2 = client.get(f"/api/v1/executions/{execution_id}/audit-logs")
    assert response2.status_code == 200
    data = response2.json()
    assert len(data) == 2
    assert data[0]["created_at"] <= data[1]["created_at"]


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
    assert len(resp1.json()) == 1
    assert len(resp2.json()) == 1
    assert resp1.json()[0]["message"] == "m1"
    assert resp2.json()[0]["message"] == "m2"


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
