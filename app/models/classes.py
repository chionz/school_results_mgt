from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.models.base_model import BaseTableModel


class Class(BaseTableModel):
    __tablename__ = "classes"

    name = Column(String, unique=True, nullable=False)
    form_teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    students = relationship("Student", back_populates="class_", cascade="all, delete-orphan")
    class_subjects = relationship("ClassSubject", back_populates="class_", cascade="all, delete-orphan")
    form_teacher = relationship("User", back_populates="managed_classes")
