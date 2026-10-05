from datetime import datetime
from pydantic import BaseModel, Field


class DutyCreate(BaseModel):
    pharmacy_id: str
    branch_id: str
    city: str = Field(min_length=1, max_length=120)
    duty_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    start_at: datetime
    end_at: datetime
    source: str = Field(min_length=1, max_length=255)


class DutyOut(BaseModel):
    id: str
    city: str
    duty_date: str
    duty_start_at: datetime
    duty_end_at: datetime
    status: str
    verification_status: str

    model_config = {"from_attributes": True}


class PublicDutyOut(BaseModel):
    id: str
    city: str
    pharmacy_id: str
    pharmacy_display_name: str
    branch_display_name: str
    address_summary: str | None
    phone: str | None
    duty_date: str
    duty_start_at: datetime
    duty_end_at: datetime
    last_verified_at: datetime | None

    model_config = {"from_attributes": True}


class DutyUpdate(BaseModel):
    branch_id: str
    city: str = Field(min_length=1, max_length=120)
    duty_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    start_at: datetime
    end_at: datetime
    source: str = Field(min_length=1, max_length=255)


class DutyBatchCreate(BaseModel):
    entries: list[DutyCreate] = Field(min_length=1, max_length=31)
