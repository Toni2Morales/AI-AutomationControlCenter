"""Pruebas de concurrencia real contra PostgreSQL.

Estas pruebas usan un contenedor PostgreSQL efímero y aislado. No reutilizan la
base de datos local de desarrollo ni ningún volumen existente.

La sincronización es explícita:

1. La primera transacción adquiere el bloqueo de fila y se detiene justo antes
   de su ``commit``.
2. La segunda transacción arranca y se comprueba en ``pg_locks`` que está
   realmente esperando un bloqueo.
3. Solo entonces se permite el ``commit`` de la primera.

Así no se asume que dos hilos "probablemente" se ejecutan a la vez.

La semántica depende del orden: si ``cancelled`` confirma primero, un
``running`` posterior se rechaza porque el estado ya es terminal. Si ``running``
confirma primero, la transición posterior ``running -> cancelled`` es válida.
"""

from __future__ import annotations

import threading
import time

import pytest
from docker import from_env as docker_from_env
from docker.errors import DockerException
from sqlalchemy import create_engine, event, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.community.postgres import PostgresContainer

from app.core.database import Base
from app.crud import execution as execution_crud
from app.crud.execution import (
    InvalidExecutionTransitionError,
    create_execution,
    update_execution_status,
)
from app.models.audit_log import AuditLog
from app.models.execution import Execution
from app.schemas.execution import ExecutionCreate


@pytest.fixture(scope="session")
def postgres_engine():
    """Arrancar un PostgreSQL efímero y crear el esquema de pruebas."""
    client = None
    try:
        client = docker_from_env()
        client.ping()
    except (DockerException, OSError) as exc:
        pytest.skip(f"Docker no disponible para las pruebas con Testcontainers: {exc}")
    finally:
        if client is not None:
            client.close()

    container = PostgresContainer(
        "postgres:16",
        username="aacc_test",
        password="aacc_test",
        dbname="aacc_test",
        driver="psycopg",
    )
    # Docker SDK acepta (dirección, puerto) en este mapping y Testcontainers lo
    # reenvía tal cual al crear el contenedor. El puerto 0 deja que Docker elija
    # uno libre, pero el bind se limita a la interfaz local.
    container.ports[str(container.port)] = ("127.0.0.1", 0)  # type: ignore[assignment]

    engine = None
    # Si Docker responde, los fallos de arranque, configuración o esquema deben
    # quedar visibles como errores de la prueba, no convertirse en omisiones.
    # El finally cubre también el arranque parcial: Testcontainers debe intentar
    # retirar el contenedor aunque ``start()`` falle a mitad.
    try:
        container.start()
        engine = create_engine(
            container.get_connection_url(host="127.0.0.1"),
            pool_pre_ping=True,
        )
        Base.metadata.create_all(bind=engine)
        yield engine
    finally:
        try:
            if engine is not None:
                engine.dispose()
        finally:
            container.stop()


@pytest.fixture()
def session_factory(postgres_engine):
    """Fábrica de sesiones independientes para cada transacción."""
    return sessionmaker(autocommit=False, autoflush=False, bind=postgres_engine)


@pytest.fixture(autouse=True)
def clean_test_database(postgres_engine):
    """Limpiar solo el contenedor efímero de pruebas antes de cada test."""
    with postgres_engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE audit_logs, executions RESTART IDENTITY CASCADE"))
    yield


def _create_pending(session_factory) -> int:
    with session_factory() as db:
        execution = create_execution(db, ExecutionCreate())
        return execution.id


def _read_status_and_events(session_factory, execution_id: int) -> tuple[str, list[str]]:
    with session_factory() as db:
        execution = db.get(Execution, execution_id)
        assert execution is not None
        events = db.scalars(
            select(AuditLog).where(AuditLog.execution_id == execution_id).order_by(AuditLog.id)
        ).all()
        return execution.status, [item.event_type for item in events]


def _wait_for_blocked_transaction(postgres_engine, waiting_pid: int, timeout: float = 10.0) -> None:
    """Esperar el bloqueo concreto de la segunda transacción sobre ``executions``."""
    lock_query = text(
        """
        SELECT count(*)
        FROM pg_locks AS locks
        JOIN pg_stat_activity AS activity ON activity.pid = locks.pid
        LEFT JOIN pg_class AS relation ON relation.oid = locks.relation
        WHERE locks.pid = :waiting_pid
          AND NOT locks.granted
          AND activity.datname = current_database()
          AND (
              locks.locktype = 'transactionid'
              OR (
                  locks.locktype IN ('relation', 'tuple')
                  AND relation.relname = 'executions'
              )
          )
        """
    )
    deadline = time.monotonic() + timeout
    with postgres_engine.connect() as connection:
        while time.monotonic() < deadline:
            waiting = connection.execute(lock_query, {"waiting_pid": waiting_pid}).scalar_one()
            if waiting:
                return
            time.sleep(0.05)
    raise AssertionError(
        f"No se observó a la transacción {waiting_pid} esperando el bloqueo de executions"
    )


def _run_gated_transitions(
    session_factory,
    postgres_engine,
    execution_id: int,
    first_status: str,
    second_status: str,
) -> dict[str, tuple[str, str | None]]:
    """Ejecutar dos transiciones con solapamiento forzado y controlado."""
    first_reached_commit = threading.Event()
    release_first = threading.Event()
    second_ready = threading.Event()
    second_pid: dict[str, int] = {}
    results: dict[str, tuple[str, str | None]] = {}
    second_thread: threading.Thread | None = None

    first_session = session_factory()

    def pause_before_commit(session: Session) -> None:
        first_reached_commit.set()
        if not release_first.wait(timeout=15):
            raise TimeoutError("La primera transacción no fue liberada a tiempo")

    event.listen(first_session, "before_commit", pause_before_commit)

    def run_first() -> None:
        try:
            execution = update_execution_status(first_session, execution_id, first_status)
            results["first"] = ("ok", execution.status if execution is not None else None)
        except InvalidExecutionTransitionError as exc:
            results["first"] = ("invalid", str(exc))
        except Exception as exc:  # pragma: no cover - solo diagnóstico
            results["first"] = ("error", repr(exc))
        finally:
            first_session.close()

    first_thread = threading.Thread(target=run_first, name="first-transition")
    first_thread.start()
    try:
        assert first_reached_commit.wait(timeout=15), (
            "La primera transición no llegó al punto de commit"
        )

        def run_second() -> None:
            second_session = session_factory()
            try:
                # Identificar la conexión concreta que va a esperar el bloqueo.
                pid = second_session.execute(text("SELECT pg_backend_pid()")).scalar_one()
                second_pid["value"] = int(pid)
                second_ready.set()

                execution = update_execution_status(second_session, execution_id, second_status)
                results["second"] = (
                    "ok",
                    execution.status if execution is not None else None,
                )
            except InvalidExecutionTransitionError as exc:
                results["second"] = ("invalid", str(exc))
            except Exception as exc:  # pragma: no cover - solo diagnóstico
                results["second"] = ("error", repr(exc))
            finally:
                second_session.close()

        second_thread = threading.Thread(target=run_second, name="second-transition")
        second_thread.start()
        assert second_ready.wait(timeout=15), "La segunda transacción no inició"
        try:
            _wait_for_blocked_transaction(postgres_engine, second_pid["value"])
        finally:
            release_first.set()

        first_thread.join(timeout=15)
        second_thread.join(timeout=15)
        assert not first_thread.is_alive(), "La primera transición no terminó"
        assert not second_thread.is_alive(), "La segunda transición no terminó"
    finally:
        release_first.set()
        first_thread.join(timeout=15)
        if second_thread is not None:
            second_thread.join(timeout=15)
        event.remove(first_session, "before_commit", pause_before_commit)

    return results


def test_concurrent_identical_transitions_are_idempotent(session_factory, postgres_engine):
    execution_id = _create_pending(session_factory)

    results = _run_gated_transitions(
        session_factory, postgres_engine, execution_id, "running", "running"
    )

    assert results["first"] == ("ok", "running")
    assert results["second"] == ("ok", "running")

    status, events = _read_status_and_events(session_factory, execution_id)
    assert status == "running"
    assert events == ["execution.created", "execution.started"]


def test_concurrent_terminal_transitions_only_one_wins(session_factory, postgres_engine):
    execution_id = _create_pending(session_factory)
    with session_factory() as db:
        update_execution_status(db, execution_id, "running")

    results = _run_gated_transitions(
        session_factory, postgres_engine, execution_id, "completed", "failed"
    )

    assert results["first"] == ("ok", "completed")
    assert results["second"][0] == "invalid"

    status, events = _read_status_and_events(session_factory, execution_id)
    assert status == "completed"
    assert events == [
        "execution.created",
        "execution.started",
        "execution.completed",
    ]


def test_concurrent_cancel_then_start_rejects_start(session_factory, postgres_engine):
    execution_id = _create_pending(session_factory)

    # En este orden, ``cancelled`` confirma primero y deja la ejecución terminal.
    # La solicitud posterior ``pending -> running`` debe rechazarse.
    results = _run_gated_transitions(
        session_factory, postgres_engine, execution_id, "cancelled", "running"
    )

    assert results["first"] == ("ok", "cancelled")
    assert results["second"][0] == "invalid"

    status, events = _read_status_and_events(session_factory, execution_id)
    assert status == "cancelled"
    assert events == ["execution.created", "execution.cancelled"]


def test_concurrent_start_then_cancel_produces_started_and_cancelled(
    session_factory, postgres_engine
):
    execution_id = _create_pending(session_factory)

    # En el orden inverso, ``running`` confirma primero y ``running -> cancelled``
    # es una transición válida. No se afirma que solo una transición pueda ganar.
    results = _run_gated_transitions(
        session_factory, postgres_engine, execution_id, "running", "cancelled"
    )

    assert results["first"] == ("ok", "running")
    assert results["second"] == ("ok", "cancelled")

    status, events = _read_status_and_events(session_factory, execution_id)
    assert status == "cancelled"
    assert events == [
        "execution.created",
        "execution.started",
        "execution.cancelled",
    ]
    transition_events = [event for event in events if event != "execution.created"]
    assert transition_events == ["execution.started", "execution.cancelled"]


def test_audit_failure_rolls_back_status(session_factory, monkeypatch):
    execution_id = _create_pending(session_factory)

    def failing_audit_log(*args, **kwargs):
        raise RuntimeError("fallo simulado al registrar auditoría")

    monkeypatch.setattr(execution_crud, "AuditLog", failing_audit_log)

    with session_factory() as db:
        with pytest.raises(RuntimeError):
            update_execution_status(db, execution_id, "running")

    status, events = _read_status_and_events(session_factory, execution_id)
    assert status == "pending"
    assert events == ["execution.created"]


def test_commit_failure_rolls_back_status_and_audit(session_factory, monkeypatch):
    execution_id = _create_pending(session_factory)
    db = session_factory()
    original_rollback = db.rollback
    rollback_calls = 0

    def failing_commit() -> None:
        # Enviar el UPDATE y el INSERT antes de simular el fallo de confirmación.
        db.flush()

        # Leer dentro de la misma transacción demuestra que ambos cambios están
        # preparados; después comprobaremos que el rollback los elimina.
        status_in_transaction = db.execute(
            select(Execution.status).where(Execution.id == execution_id)
        ).scalar_one()
        events_in_transaction = db.scalars(
            select(AuditLog.event_type)
            .where(AuditLog.execution_id == execution_id)
            .order_by(AuditLog.id)
        ).all()
        assert status_in_transaction == "running"
        assert events_in_transaction == ["execution.created", "execution.started"]

        raise RuntimeError("fallo simulado de commit")

    def tracking_rollback() -> None:
        nonlocal rollback_calls
        rollback_calls += 1
        original_rollback()

    monkeypatch.setattr(db, "commit", failing_commit)
    monkeypatch.setattr(db, "rollback", tracking_rollback)
    try:
        with pytest.raises(RuntimeError, match="fallo simulado de commit"):
            update_execution_status(db, execution_id, "running")
        assert rollback_calls == 1
    finally:
        db.close()

    status, events = _read_status_and_events(session_factory, execution_id)
    assert status == "pending"
    assert events == ["execution.created"]


def test_database_rejects_invalid_status(session_factory):
    with session_factory() as db:
        db.add(Execution(status="unknown"))
        with pytest.raises(IntegrityError):
            db.commit()
