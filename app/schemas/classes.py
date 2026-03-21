from pydantic import BaseModel
from typing import Optional, Union, List


class CreateSchema(BaseModel):
    
    name: str
