from pydantic import BaseModel
from typing import Optional, Union, List


class StudentCreateSchema(BaseModel):
    
    name: str 
    class_id: int 
    class_number: int
