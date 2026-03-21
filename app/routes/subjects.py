from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.subjects import addSubjectSchema, subjectClassSchema
from app.services.subjects import subject_service

# This maps and tags our users routes 
subjectrouter = APIRouter(prefix="/subjects", tags=["Subject"])

# This is an endpoint
@subjectrouter.post("/")
def create_subject(schema: addSubjectSchema, db: Session = Depends(get_db)):
    db_subject = subject_service.create(db=db, schema=schema)
    return db_subject


@subjectrouter.post("/class_subjects/")
def add_subject_to_class(schema: subjectClassSchema, db: Session = Depends(get_db)):
    # Check if already linked
    add = subject_service.add_subject_to_class(db=db, schema=schema)
    return add

@subjectrouter.get("/class_subjects/{class_id}")
def get_subjects_by_class(class_id: int, db: Session = Depends(get_db)):
    get_subjects = subject_service.get_subjects_linked_to_class(db=db, class_id=class_id)
    return get_subjects

@subjectrouter.get("/all_subjects")
def get_all_subjects(db: Session = Depends(get_db)):
    subjects = subject_service.get_all_subjects(db=db)
    return subjects