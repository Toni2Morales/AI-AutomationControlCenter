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


class ExecutionCreate(BaseModel):
    """Esquema para crear una ejecución.

    Solo admite campos escribibles por el cliente. Los campos gestionados por
    el servidor (``id``, ``status``, ``started_at``, ``finished_at``,
    ``created_at`` y ``updated_at``) se ignoran si se envían.
    """

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

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
