from sqlalchemy import Column, Float, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base_model import BaseTableModel


class Score(BaseTableModel):
    __tablename__ = "scores"
    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", name="uq_scores_student_subject"),
    )

    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)

    test1 = Column(Float, default=0.0, nullable=False)
    test2 = Column(Float, default=0.0, nullable=False)
    test3 = Column(Float, default=0.0, nullable=False)
    exam = Column(Float, default=0.0, nullable=False)

    student = relationship("Student", back_populates="scores")
    subject = relationship("Subject", back_populates="scores")
