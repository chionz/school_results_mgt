from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base_model import BaseTableModel

class Score(BaseTableModel):
    __tablename__ = "scores"

    student_id = Column(Integer, ForeignKey("students.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))

    test1 = Column(Float, default=0.0)
    test2 = Column(Float, default=0.0)
    test3 = Column(Float, default=0.0)
    exam = Column(Float, default=0.0)

    # Relationships
    student = relationship("Student", back_populates="scores")
    subject = relationship("Subject", back_populates="scores")