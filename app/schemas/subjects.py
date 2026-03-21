from pydantic import BaseModel
from typing import Optional, Union, List


class addSubjectSchema(BaseModel):
    
    name: str

class subjectClassSchema(BaseModel):
    
    class_id: int
    subject_id: int