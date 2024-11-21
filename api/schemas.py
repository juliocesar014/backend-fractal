from ninja import Schema
from pydantic import EmailStr
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
