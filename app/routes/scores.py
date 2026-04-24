from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.scores import scoreSchema
from app.security import get_current_user
from app.services.scores import score_service

scoresrouter = APIRouter(prefix="/scores", tags=["Scores"])


@scoresrouter.post("/")
def add_or_update_score(
    schema: scoreSchema,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    score = score_service.add_update_score(db=db, schema=schema, current_user=current_user)
    return score


@scoresrouter.get("/entry/{class_id}")
def get_score_entry(
    class_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = score_service.get_score_entry(db=db, class_id=class_id, current_user=current_user)
    return result


@scoresrouter.get("/class-results/{class_id}")
def get_class_results(
    class_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = score_service.get_class_results(db=db, class_id=class_id, current_user=current_user)
    return result


@scoresrouter.get("/student-result/{student_id}")
def get_student_result(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = score_service.get_student_score(db=db, student_id=student_id, current_user=current_user)
    return result


@scoresrouter.get("/{student_id}")
def get_student_result_legacy(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    result = score_service.get_student_score(db=db, student_id=student_id, current_user=current_user)
    return result
