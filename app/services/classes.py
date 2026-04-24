from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.classes import Class
from app.models.subjects import ClassSubject
from app.models.users import User
from app.schemas.classes import CreateSchema
from app.services.users import user_service


class ClassService:
    def create(self, db: Session, schema: CreateSchema):
        if db.query(Class).filter(Class.name == schema.name.strip()).first():
            raise HTTPException(status_code=409, detail="Class already exists")

        teacher_id = schema.form_teacher_id
        if teacher_id:
            user_service.get_teacher(db, teacher_id)

        class_create = Class(name=schema.name.strip(), form_teacher_id=teacher_id)
        db.add(class_create)
        db.commit()
        db.refresh(class_create)
        return class_create

    def get_by_id(self, db: Session, class_id: int) -> Class:
        class_obj = db.query(Class).filter(Class.id == class_id).first()
        if not class_obj:
            raise HTTPException(status_code=404, detail="Class not found")
        return class_obj

    def fetch_all(self, db: Session, current_user: User):
        query = db.query(Class)
        if not current_user.is_admin:
            query = (
                query.outerjoin(ClassSubject, ClassSubject.class_id == Class.id)
                .filter(
                    or_(
                        Class.form_teacher_id == current_user.id,
                        ClassSubject.teacher_id == current_user.id,
                    )
                )
                .distinct()
            )

        return query.order_by(Class.name.asc()).all()

    def assign_form_teacher(self, db: Session, class_id: int, teacher_id: int | None):
        class_obj = self.get_by_id(db, class_id)
        if teacher_id is not None:
            user_service.get_teacher(db, teacher_id)
        class_obj.form_teacher_id = teacher_id
        db.add(class_obj)
        db.commit()
        db.refresh(class_obj)
        return class_obj

    def can_manage_students(self, current_user: User, class_obj: Class) -> bool:
        return current_user.is_admin or class_obj.form_teacher_id == current_user.id

    def can_view_class_results(self, current_user: User, class_obj: Class) -> bool:
        return current_user.is_admin or class_obj.form_teacher_id == current_user.id

    def can_edit_subject_scores(self, current_user: User, class_id: int, subject_id: int, db: Session) -> bool:
        if current_user.is_admin:
            return True
        return (
            db.query(ClassSubject)
            .filter(
                ClassSubject.class_id == class_id,
                ClassSubject.subject_id == subject_id,
                ClassSubject.teacher_id == current_user.id,
            )
            .first()
            is not None
        )

    def serialize_class(self, class_obj: Class):
        return {
            "id": class_obj.id,
            "name": class_obj.name,
            "form_teacher_id": class_obj.form_teacher_id,
            "form_teacher_name": class_obj.form_teacher.full_name if class_obj.form_teacher else None,
            "student_count": len(class_obj.students),
            "subject_count": len(class_obj.class_subjects),
        }

class_service = ClassService()
