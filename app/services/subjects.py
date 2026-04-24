from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.subjects import ClassSubject, Subject
from app.schemas.subjects import addSubjectSchema, subjectClassSchema
from app.services.classes import class_service
from app.services.users import user_service


class SubjectService:
    def create(self, db: Session, schema: addSubjectSchema):
        if db.query(Subject).filter(Subject.name == schema.name.strip()).first():
            raise HTTPException(status_code=409, detail="Subject already exists")
        create_subject = Subject(name=schema.name.strip())
        db.add(create_subject)
        db.commit()
        db.refresh(create_subject)
        return create_subject

    def get_all_subjects(self, db: Session):
        subjects = db.query(Subject).order_by(Subject.name.asc()).all()
        return subjects

    def add_subject_to_class(self, db: Session, schema: subjectClassSchema):
        class_service.get_by_id(db, schema.class_id)
        subject = db.query(Subject).filter(Subject.id == schema.subject_id).first()
        if not subject:
            raise HTTPException(status_code=404, detail="Subject not found")

        if schema.teacher_id is not None:
            user_service.get_teacher(db, schema.teacher_id)

        exists = (
            db.query(ClassSubject)
            .filter_by(class_id=schema.class_id, subject_id=schema.subject_id)
            .first()
        )
        if exists:
            exists.teacher_id = schema.teacher_id
            db.add(exists)
            db.commit()
            db.refresh(exists)
            return exists

        add_subject = ClassSubject(
            class_id=schema.class_id,
            subject_id=schema.subject_id,
            teacher_id=schema.teacher_id,
        )
        db.add(add_subject)
        db.commit()
        db.refresh(add_subject)
        return add_subject

    def get_subjects_linked_to_class(self, db: Session, class_id: int):
        links = (
            db.query(ClassSubject)
            .filter(ClassSubject.class_id == class_id)
            .join(Subject, Subject.id == ClassSubject.subject_id)
            .order_by(Subject.name.asc())
            .all()
        )
        return links

    def serialize_assignment(self, link: ClassSubject):
        return {
            "id": link.id,
            "class_id": link.class_id,
            "class_name": link.class_.name if link.class_ else None,
            "subject_id": link.subject_id,
            "subject_name": link.subject.name if link.subject else None,
            "teacher_id": link.teacher_id,
            "teacher_name": link.teacher.full_name if link.teacher else None,
        }

subject_service = SubjectService()
