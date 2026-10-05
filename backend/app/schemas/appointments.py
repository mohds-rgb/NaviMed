from datetime import datetime
from pydantic import BaseModel, Field


class HoldCreate(BaseModel):
    slot_id: str


class AppointmentCreate(BaseModel):
    hold_id: str


class AppointmentReschedule(BaseModel):
    new_slot_id: str


class AppointmentCancel(BaseModel):
    reason: str | None = Field(default=None, max_length=255)


class AppointmentOut(BaseModel):
    id: str
    status: str
    request_status: str
    scheduled_start_at: datetime
    scheduled_end_at: datetime
    provider_id: str
    clinic_id: str
    slot_id: str
    reschedule_of_appointment_id: str | None = None

    model_config = {"from_attributes": True}


class HoldOut(BaseModel):
    id: str
    slot_id: str
    expires_at: datetime

    model_config = {"from_attributes": True}
