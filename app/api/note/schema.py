from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NoteBase(BaseModel):
    note: str
    user_id: int

    class Config:
        orm_mode = True


class NoteCreate(NoteBase):
    pass


class NoteUpdate(NoteBase):
    note: Optional[str] = None


class NoteInDBBase(NoteBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class NoteResponse(NoteInDBBase):
    pass
