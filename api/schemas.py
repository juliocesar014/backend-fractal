from ninja import Schema
from pydantic import EmailStr, BaseModel, Field
from typing import Optional
from datetime import datetime

from api.models import User


class UserSchema(Schema):
    id: int
    username: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    creation_date: datetime
    modification_date: datetime


class CreateUserSchema(Schema):
    username: str
    email: EmailStr
    first_name: Optional[str]
    last_name: Optional[str]
    password: str
    role: str

    @staticmethod
    def validate_role(role: str):
        if role not in [User.RoleTypes.ADMIN, User.RoleTypes.PARTICIPANT]:
            raise ValueError(
                "Invalid Role. Role must be 'admin' or 'participant'")
        return role


class UpdateUserSchema(Schema):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[EmailStr]
    role: Optional[str]


class ExamSchema(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: datetime
    end_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreateExamSchema(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str]
    start_date: datetime
    end_date: datetime


class UpdateExamSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
