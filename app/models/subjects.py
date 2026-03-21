from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base_model import BaseTableModel

class Subject(BaseTableModel):
    __tablename__ = "subjects"

    name = Column(String, unique=True)

    # Relationships
    class_subjects = relationship("ClassSubject", back_populates="subject")
    scores = relationship("Score", back_populates="subject")


class ClassSubject(BaseTableModel):
    __tablename__ = "class_subjects"

    class_id = Column(Integer, ForeignKey("classes.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))

    # Relationships
    class_ = relationship("Class", back_populates="class_subjects")
    subject = relationship("Subject", back_populates="class_subjects")