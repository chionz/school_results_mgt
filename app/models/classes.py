from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.models.base_model import BaseTableModel

class Class(BaseTableModel):
    __tablename__ = "classes"

    name = Column(String, unique=True)

    # Relationships
    students = relationship("Student", back_populates="class_")
    class_subjects = relationship("ClassSubject", back_populates="class_")