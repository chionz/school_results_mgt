from pydantic import BaseModel, Field


class LoginSchema(BaseModel):
    username: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=6, max_length=120)


class TeacherCreateSchema(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    username: str = Field(min_length=2, max_length=60)
    email: str = Field(min_length=5, max_length=120)
    password: str = Field(min_length=6, max_length=120)
