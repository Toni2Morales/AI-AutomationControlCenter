from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExecutionBase(BaseModel):
    status: str = Field(default="pending")
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_message: str | None = None
    trigger_source: str | None = Field(default=None, max_length=50)
    metadata: dict | None = None


class ExecutionCreate(ExecutionBase):
    pass


class ExecutionUpdate(BaseModel):
    status: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_message: str | None = None
    trigger_source: str | None = Field(default=None, max_length=50)
    metadata: dict | None = None


class ExecutionRead(ExecutionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class AuditLogBase(BaseModel):
    execution_id: int | None = None
    event_type: str = Field(max_length=50)
    message: str
    details: dict | None = None


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogRead(AuditLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
