import os
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.models.users import User
from app.schemas.users import TeacherCreateSchema
from app.security import hash_password, verify_password


class UserService:
    def bootstrap_admin(self, db: Session) -> Optional[User]:
        try:
            existing_user = db.query(User).first()
        except OperationalError:
            db.rollback()
            return None

        if existing_user:
            return existing_user

        admin = User(
            full_name=os.getenv("BOOTSTRAP_ADMIN_NAME", "System Administrator"),
            username=os.getenv("BOOTSTRAP_ADMIN_USERNAME", "admin"),
            email=os.getenv("BOOTSTRAP_ADMIN_EMAIL", "admin@school.local"),
            password_hash=hash_password(os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "admin12345")),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        try:
            db.commit()
            db.refresh(admin)
            return admin
        except IntegrityError:
            db.rollback()
            return db.query(User).filter(User.role == "admin").first()

    def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
        user = (
            db.query(User)
            .filter((User.username == username) | (User.email == username))
            .filter(User.is_active.is_(True))
            .first()
        )
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    def create_teacher(self, db: Session, schema: TeacherCreateSchema) -> User:
        teacher = User(
            full_name=schema.full_name.strip(),
            username=schema.username.strip().lower(),
            email=schema.email.strip().lower(),
            password_hash=hash_password(schema.password),
            role="teacher",
            is_active=True,
        )
        db.add(teacher)
        try:
            db.commit()
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Teacher username or email already exists",
            ) from exc
        db.refresh(teacher)
        return teacher

    def list_teachers(self, db: Session):
        return db.query(User).filter(User.role == "teacher").order_by(User.full_name.asc()).all()

    def get_teacher(self, db: Session, teacher_id: int) -> User:
        teacher = db.query(User).filter(User.id == teacher_id, User.role == "teacher").first()
        if not teacher:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
        return teacher


user_service = UserService()
