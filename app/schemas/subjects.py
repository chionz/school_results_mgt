from typing import Optional

from pydantic import BaseModel, Field


class addSubjectSchema(BaseModel):
    name: str = Field(min_length=2, max_length=80)

class subjectClassSchema(BaseModel):
    class_id: int
    subject_id: int
    teacher_id: Optional[int] = None
