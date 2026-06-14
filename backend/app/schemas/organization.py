import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class OrganizationUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    industry: str | None = Field(None, max_length=50)


class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    industry: str = "construccion_mineria"
    created_at: datetime
    model_config = {"from_attributes": True}


class OrgMemberResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    email: str
    full_name: str | None
    role: str


class UserOrgMembership(BaseModel):
    org_id: uuid.UUID
    org_name: str
    role: str


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str | None
    organizations: list[UserOrgMembership]
