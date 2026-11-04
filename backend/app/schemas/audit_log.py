from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuditLogBase(BaseModel):
    execution_id: int | None = Field(default=None, description="ID de ejecución asociado")
    event_type: str = Field(max_length=50, description="Tipo de evento")
    message: str = Field(description="Mensaje del evento")
    details: dict | None = Field(default=None, description="Detalles adicionales")


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogRead(AuditLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description="Identificador único")
    created_at: datetime = Field(description="Fecha de creación (UTC)")
