from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.users import TeacherCreateSchema
from app.security import get_current_user, require_admin
from app.services.users import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/teachers")
def get_teachers(
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    teachers = user_service.list_teachers(db=db)
    return [
        {
            "id": teacher.id,
            "full_name": teacher.full_name,
            "username": teacher.username,
            "email": teacher.email,
        }
        for teacher in teachers
    ]


@router.post("/teachers")
def create_teacher(
    schema: TeacherCreateSchema,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    teacher = user_service.create_teacher(db=db, schema=schema)
    return {
        "id": teacher.id,
        "full_name": teacher.full_name,
        "username": teacher.username,
        "email": teacher.email,
        "role": teacher.role,
    }
