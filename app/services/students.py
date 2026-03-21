
from fastapi import Depends, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.students import Student
from app.schemas.students import StudentCreateSchema


class StudentService():
    """Class service"""
    
    def create(self, db: Session, schema: StudentCreateSchema):
        create_student = Student(
            name=schema.name, 
            class_id=schema.class_id, 
            class_number=schema.class_number
            )
        db.add(create_student)
        db.commit()
        db.refresh(create_student)
        return create_student

    def fetch(self):
        pass
    
    def fetch_by_class_id(self, db: Session, class_id: int):
        students = db.query(Student).filter(Student.class_id == class_id).all()
        return students

    def update(self):
        pass

    
    def delete(self):
        pass

student_service = StudentService()




