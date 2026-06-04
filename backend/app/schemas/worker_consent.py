import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

ConsentStatus = Literal["pending", "informed", "granted", "revoked"]
ConsentMethod = Literal["verbal", "written", "email", "contract", "platform"]


class WorkerConsentUpsert(BaseModel):
    status: ConsentStatus
    method: ConsentMethod | None = None
    consent_date: datetime | None = None
    notes: str | None = None


class WorkerConsentResponse(BaseModel):
    worker_id: uuid.UUID
    status: ConsentStatus = "pending"
    method: ConsentMethod | None = None
    consent_date: datetime | None = None
    notes: str | None = None
    recorded_by_name: str | None = None
    updated_at: datetime | None = None
