from pydantic import BaseModel, Field


class AppointmentNoteCreate(BaseModel):
    note_body: str = Field(min_length=1, max_length=1000)
    visibility: str = Field(default="internal", pattern=r"^internal$")


class AppointmentNoteOut(BaseModel):
    id: str
    appointment_id: str
    author_user_id: str
    note_body: str
    visibility: str

    model_config = {"from_attributes": True}
