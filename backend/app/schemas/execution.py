from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class ExecutionBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    status: str = Field(default="pending", description="Estado de la ejecución")
    started_at: datetime | None = Field(default=None, description="Fecha de inicio (UTC)")
    finished_at: datetime | None = Field(default=None, description="Fecha de finalización (UTC)")
    error_message: str | None = Field(default=None, description="Mensaje de error")
    trigger_source: str | None = Field(
        default=None, max_length=50, description="Origen del disparo"
    )
    metadata: dict | None = Field(
        default=None,
        validation_alias=AliasChoices("metadata", "extra_metadata"),
        serialization_alias="metadata",
        description="Metadatos adicionales",
    )


class ExecutionCreate(ExecutionBase):
    """Esquema para crear una ejecución."""


class ExecutionUpdate(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    status: str | None = Field(default=None, description="Estado de la ejecución")
    started_at: datetime | None = Field(default=None, description="Fecha de inicio (UTC)")
    finished_at: datetime | None = Field(default=None, description="Fecha de finalización (UTC)")
    error_message: str | None = Field(default=None, description="Mensaje de error")
    trigger_source: str | None = Field(
        default=None, max_length=50, description="Origen del disparo"
    )
    metadata: dict | None = Field(
        default=None,
        validation_alias=AliasChoices("metadata", "extra_metadata"),
        serialization_alias="metadata",
        description="Metadatos adicionales",
    )


class ExecutionRead(ExecutionBase):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: int = Field(description="Identificador único")
    created_at: datetime = Field(description="Fecha de creación (UTC)")
    updated_at: datetime = Field(description="Fecha de actualización (UTC)")
