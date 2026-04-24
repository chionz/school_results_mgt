from typing import Optional

from pydantic import BaseModel, Field


class scoreSchema(BaseModel):
    student_id: int
    subject_id: int
    test1: Optional[float] = Field(default=None, ge=0, le=100)
    test2: Optional[float] = Field(default=None, ge=0, le=100)
    test3: Optional[float] = Field(default=None, ge=0, le=100)
    exam: Optional[float] = Field(default=None, ge=0, le=100)
