from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.orm import relationship

from app.models.base_model import BaseTableModel


class User(BaseTableModel):
    __tablename__ = "users"

    full_name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="teacher")
    is_active = Column(Boolean, nullable=False, default=True)
    session_token = Column(String, unique=True, index=True, nullable=True)
    session_expires_at = Column(DateTime(timezone=True), nullable=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    managed_classes = relationship("Class", back_populates="form_teacher")
    teaching_assignments = relationship("ClassSubject", back_populates="teacher")

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"
