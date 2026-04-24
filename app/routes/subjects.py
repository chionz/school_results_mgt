from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.subjects import addSubjectSchema, subjectClassSchema
from app.security import get_current_user, require_admin
from app.services.subjects import subject_service

subjectrouter = APIRouter(prefix="/subjects", tags=["Subject"])


@subjectrouter.post("/")
def create_subject(
    schema: addSubjectSchema,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    db_subject = subject_service.create(db=db, schema=schema)
    return {"id": db_subject.id, "name": db_subject.name}


@subjectrouter.post("/class_subjects/")
def add_subject_to_class(
    schema: subjectClassSchema,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    add = subject_service.add_subject_to_class(db=db, schema=schema)
    return subject_service.serialize_assignment(add)


@subjectrouter.get("/class_subjects/{class_id}")
def get_subjects_by_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    get_subjects = subject_service.get_subjects_linked_to_class(db=db, class_id=class_id)
    return [subject_service.serialize_assignment(link) for link in get_subjects]


@subjectrouter.get("/all_subjects")
def get_all_subjects(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    subjects = subject_service.get_all_subjects(db=db)
    return [{"id": subject.id, "name": subject.name} for subject in subjects]
