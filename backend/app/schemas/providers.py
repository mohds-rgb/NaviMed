from datetime import datetime
from pydantic import BaseModel, Field


class PublicProviderOut(BaseModel):
    id: str
    display_name: str
    specialty: str
    bio: str | None

    model_config = {"from_attributes": True}


class ProviderOut(BaseModel):
    id: str
    display_name: str
    specialty: str
    bio: str | None
    verification_status: str

    model_config = {"from_attributes": True}


class ClinicOut(BaseModel):
    id: str
    provider_id: str
    name: str
    city: str
    area: str | None
    address_summary: str | None
    phone_public: str | None
    booking_policy: str
    policy_version: int

    model_config = {"from_attributes": True}


class SlotOut(BaseModel):
    id: str
    start_at: datetime
    end_at: datetime
    status: str

    model_config = {"from_attributes": True}


class ClinicCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    city: str = Field(min_length=1, max_length=120)
    area: str | None = Field(default=None, max_length=120)
    address_summary: str | None = Field(default=None, max_length=255)
    phone_public: str | None = Field(default=None, max_length=32)
    booking_policy: str = Field(default="provider_confirmation", pattern=r"^(instant|provider_confirmation)$")
