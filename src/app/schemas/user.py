import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=120)
    role: str | None = Field(min_length=0,max_length=120)
    

class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime
    password_hash: str
    role:str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserRoleUpdate(BaseModel):
    email: EmailStr
    role: str | None