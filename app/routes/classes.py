from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.classes import AssignFormTeacherSchema, CreateSchema
from app.security import get_current_user, require_admin
from app.services.classes import class_service

classrouter = APIRouter(prefix="/classes", tags=["Class"])


@classrouter.post("/")
def create_class(
    schema: CreateSchema,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    db_class = class_service.create(db, schema=schema)
    return class_service.serialize_class(db_class)


@classrouter.get("/list")
def all_class(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    all_classes = class_service.fetch_all(db=db, current_user=current_user)
    return [class_service.serialize_class(class_obj) for class_obj in all_classes]


@classrouter.put("/{class_id}/form-teacher")
def assign_form_teacher(
    class_id: int,
    schema: AssignFormTeacherSchema,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    class_obj = class_service.assign_form_teacher(
        db=db,
        class_id=class_id,
        teacher_id=schema.teacher_id,
    )
    return class_service.serialize_class(class_obj)
