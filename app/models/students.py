from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base_model import BaseTableModel

class Student(BaseTableModel):
    __tablename__ = "students"

    name = Column(String)
    class_number = Column(Integer, #unique=True
                          )
    class_id = Column(Integer, ForeignKey("classes.id"))

    # Relationships
    class_ = relationship("Class", back_populates="students")
    scores = relationship("Score", back_populates="student")