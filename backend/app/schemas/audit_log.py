from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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
