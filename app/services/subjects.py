
from fastapi import Depends, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.subjects import ClassSubject, Subject
from app.schemas.subjects import addSubjectSchema, subjectClassSchema


class SubjectService():
    """Class service"""
    
    def create(self, db: Session, schema: addSubjectSchema):
        create_subject = Subject(name=schema.name)
        db.add(create_subject)
        db.commit()
        db.refresh(create_subject)
        return create_subject

    def fetch(self):
        pass

    def get_all_subjects(self, db: Session):
        subjects = db.query(Subject).all()
        return subjects
    
    def add_subject_to_class(self, db: Session, schema: subjectClassSchema):
        exists = db.query(ClassSubject).filter_by(class_id=schema.class_id, subject_id=schema.subject_id).first()
        if exists:
            return exists

        add_subject = ClassSubject(class_id=schema.class_id, subject_id=schema.subject_id)
        db.add(add_subject)
        db.commit()
        db.refresh(add_subject)
        return add_subject
    
    def get_subjects_linked_to_class(self, db: Session, class_id: int):
        links = db.query(ClassSubject).filter(ClassSubject.class_id == class_id).all()
        subjects = [db.query(Subject).get(link.subject_id) for link in links]
        return subjects

    def update(self):
        pass

    
    def delete(self):
        pass

subject_service = SubjectService()




