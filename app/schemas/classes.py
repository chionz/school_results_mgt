from typing import Optional

from pydantic import BaseModel, Field


class CreateSchema(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    form_teacher_id: Optional[int] = None


class AssignFormTeacherSchema(BaseModel):
    teacher_id: Optional[int] = None
