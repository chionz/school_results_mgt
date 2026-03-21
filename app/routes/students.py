from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.students import StudentCreateSchema
from app.services.students import student_service

# This maps and tags our users routes 
studentrouter = APIRouter(prefix="/students", tags=["Students"])

# This is an endpoint
@studentrouter.post("/")
def create_student(schema: StudentCreateSchema, db: Session = Depends(get_db)):
    db_student = student_service.create(db=db, schema=schema)
    return db_student

@studentrouter.get("/{class_id}")
def get_students_by_class(class_id: int, db: Session = Depends(get_db)):
    students = student_service.fetch_by_class_id(db=db, class_id=class_id)
    return students