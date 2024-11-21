from pydantic import BaseModel, Field
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
        if role not in User.RoleTypes.values:
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


class QuestionSchema(BaseModel):
    id: int
    exam_id: int
    text: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreateQuestionSchema(BaseModel):
    exam_id: int
    text: str = Field(..., max_length=1000)


class UpdateQuestionSchema(BaseModel):
    text: Optional[str] = Field(None, max_length=1000)


class ChoiceSchema(BaseModel):
    id: int
    question_id: int
    text: str
    is_correct: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class CreateChoiceSchema(BaseModel):
    question_id: int
    text: str = Field(..., max_length=255)
    is_correct: bool


class UpdateChoiceSchema(BaseModel):
    text: Optional[str] = Field(None, max_length=255)
    is_correct: Optional[bool]


class ParticipantSchema(BaseModel):
    id: int
    user_id: int
    exams: list[ExamSchema]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreateParticipantSchema(BaseModel):
    user_id: int
    exam_ids: Optional[list[int]] = []


class UpdateParticipantSchema(BaseModel):
    exam_ids: Optional[list[int]] = []


class AnswerSchema(BaseModel):
    id: int
    participant_id: int
    question_id: int
    choice_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class CreateAnswerSchema(BaseModel):
    participant_id: int
    question_id: int
    choice_id: int


class UpdateAnswerSchema(BaseModel):
    choice_id: int
