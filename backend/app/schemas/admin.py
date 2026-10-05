from pydantic import BaseModel, Field


class ProviderApproval(BaseModel):
    reason: str | None = Field(default=None, max_length=255)


class EmergencyContactCreate(BaseModel):
    label: str = Field(min_length=1, max_length=180)
    phone: str = Field(min_length=3, max_length=32)
    authority_source: str = Field(min_length=1, max_length=255)
