from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class AccountOut(BaseModel):
    id: str
    email: str
    role: str
    created_at: datetime
    last_login_at: datetime | None = None

    class Config:
        from_attributes = True
