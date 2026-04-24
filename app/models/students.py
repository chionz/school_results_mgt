from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base_model import BaseTableModel


class Student(BaseTableModel):
    __tablename__ = "students"
    """ __table_args__ = (
        UniqueConstraint("class_id", "class_number", name="uq_students_class_roll"),
    ) """

    name = Column(String, nullable=False)
    class_number = Column(Integer, nullable=False)
    admission_number = Column(String, unique=True, nullable=True)
    gender = Column(String, nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)

    class_ = relationship("Class", back_populates="students")
    scores = relationship("Score", back_populates="student", cascade="all, delete-orphan")
