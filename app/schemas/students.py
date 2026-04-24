from typing import Optional

from pydantic import BaseModel, Field


class StudentCreateSchema(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    class_id: int
    class_number: int = Field(ge=1, le=9999)
    admission_number: Optional[str] = Field(default=None, max_length=60)
    gender: Optional[str] = Field(default=None, max_length=20)
