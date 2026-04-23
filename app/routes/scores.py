from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.scores import scoreSchema
from app.services.scores import score_service

# This maps and tags our users routes 
scoresrouter = APIRouter(prefix="/scores", tags=["Scores"])

# This is an endpoint
@scoresrouter.post("/")
def add_or_update_score(schema: scoreSchema, db: Session = Depends(get_db)):
    score = score_service.add_update_score(db=db, schema=schema)
    return score

@scoresrouter.get("/{student_id}")
def get_student_result(student_id: int, db: Session = Depends(get_db)):
    result = score_service.get_student_score(db=db, student_id=student_id)
    return result

@scoresrouter.get("/class-results/{class_id}")
def get_class_results(class_id: int, db: Session = Depends(get_db)):
    result = score_service.get_class_results(db=db, class_id=class_id)
    return result