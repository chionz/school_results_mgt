from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.students import StudentCreateSchema
from app.security import get_current_user
from app.services.classes import class_service
from app.services.students import student_service

studentrouter = APIRouter(prefix="/students", tags=["Students"])


@studentrouter.post("/")
def create_student(
    schema: StudentCreateSchema,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    class_obj = class_service.get_by_id(db, schema.class_id)
    if not class_service.can_manage_students(current_user, class_obj):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned form teacher or an administrator can add students",
        )
    db_student = student_service.create(db=db, schema=schema)
    return {
        "id": db_student.id,
        "name": db_student.name,
        "class_id": db_student.class_id,
        "class_number": db_student.class_number,
        "admission_number": db_student.admission_number,
        "gender": db_student.gender,
    }


@studentrouter.get("/class/{class_id}")
def get_students_by_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    class_obj = class_service.get_by_id(db, class_id)
    if not (
        class_service.can_manage_students(current_user, class_obj)
        or class_service.can_view_class_results(current_user, class_obj)
        or current_user.is_admin
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to students in this class",
        )
    students = student_service.fetch_by_class_id(db=db, class_id=class_id)
    return [
        {
            "id": student.id,
            "name": student.name,
            "class_number": student.class_number,
            "admission_number": student.admission_number,
            "gender": student.gender,
        }
        for student in students
    ]
