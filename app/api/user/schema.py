from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    balance: Optional[int] = 0
    is_superuser: Optional[bool] = False

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None


class UserInDBBase(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class UserResponse(UserInDBBase):
    pass
