from pydantic import BaseModel


class ContractStatus(BaseModel):
    """Estado de aceptación del contrato para el usuario actual."""

    current_version: str
    accepted: bool  # ¿aceptó la versión vigente?
