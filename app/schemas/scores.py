from pydantic import BaseModel
from typing import Optional, Union, List


class scoreSchema(BaseModel):

    student_id: int
    subject_id: int
    test1: Optional[float] = None
    test2: Optional[float] = None
    test3: Optional[float] = None
    exam: Optional[float] = None