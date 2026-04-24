from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base_model import BaseTableModel


class Subject(BaseTableModel):
    __tablename__ = "subjects"

    name = Column(String, unique=True, nullable=False)

    class_subjects = relationship("ClassSubject", back_populates="subject", cascade="all, delete-orphan")
    scores = relationship("Score", back_populates="subject")


class ClassSubject(BaseTableModel):
    __tablename__ = "class_subjects"
    __table_args__ = (
        UniqueConstraint("class_id", "subject_id", name="uq_class_subjects_class_subject"),
    )

    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    class_ = relationship("Class", back_populates="class_subjects")
    subject = relationship("Subject", back_populates="class_subjects")
    teacher = relationship("User", back_populates="teaching_assignments")
