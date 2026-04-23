
from fastapi import Depends, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.classes import Class
from app.models.scores import Score
from app.models.students import Student
from app.models.subjects import ClassSubject, Subject
from app.schemas.scores import scoreSchema


class ScoreService():
    """Class service"""
    
    def create(self):
        pass

    def add_update_score(self, db: Session, schema: scoreSchema):
        score = db.query(Score).filter_by(student_id=schema.student_id, subject_id=schema.subject_id).first()
        if score:
            if schema.test1 is not None:
                score.test1 = schema.test1
            if schema.test2 is not None:
                score.test2 = schema.test2
            if schema.test3 is not None:
                score.test3 = schema.test3
            if schema.exam is not None:
                score.exam = schema.exam
        else:
            score = Score(student_id=schema.student_id, 
                          subject_id=schema.subject_id, 
                          test1=schema.test1, 
                          test2=schema.test2, 
                          test3=schema.test3, 
                          exam=schema.exam
                          )
            db.add(score)
        db.commit()
        db.refresh(score)
        return score
    
    def get_student_score(self, db: Session, student_id: int):
        scores = db.query(Score).filter(Score.student_id == student_id).all()
        if not scores:
            return None
        student = scores[0].student
        result = []
        overall_total = 0

        for s in scores:
            subject = db.query(Subject).get(s.subject_id)
            total = s.test1 + s.test2 + s.test3 + s.exam
            overall_total += total

            result.append({
                "subject": subject.name,
                "test1": s.test1,
                "test2": s.test2,
                "test3": s.test3,
                "exam": s.exam,
                "total": total
            })

        overall_average = overall_total / len(scores) if scores else 0

        return {
            "student_info": {
                "id": student.id,
                "name": student.name,
                "class_id": student.class_id,
                "class_number": student.class_number
            },  
            "student_id": student_id,
            "subjects": result,
            "number_of_subjects": len(scores),
            "overall_total": overall_total,
            "overall_average": round(overall_average, 2)  
        }
    
    def get_class_results(self, db: Session, class_id: int):

        # Get class
        class_obj = db.query(Class).filter(Class.id == class_id).first()
        if not class_obj:
            return None

        # Get students in class
        students = db.query(Student).filter(Student.class_id == class_id).all()

        # Get subjects assigned to class
        subjects = (
            db.query(Subject)
            .join(ClassSubject, ClassSubject.subject_id == Subject.id)
            .filter(ClassSubject.class_id == class_id)
            .all()
        )

        student_ids = [s.id for s in students]
        subject_ids = [s.id for s in subjects]

        # Get scores only for this class students + subjects
        scores = []
        if student_ids and subject_ids:
            scores = (
                db.query(Score)
                .filter(
                    Score.student_id.in_(student_ids),
                    Score.subject_id.in_(subject_ids)
                )
                .all()
            )

        # Create quick lookup map
        score_map = {(score.student_id, score.subject_id): score for score in scores}

        # Build response and calculate total per student
        students_data = []
        totals = []

        for student in students:
            subject_results = []
            student_total = 0

            for subject in subjects:
                score = score_map.get((student.id, subject.id))

                t1 = score.test1 if score else 0
                t2 = score.test2 if score else 0
                t3 = score.test3 if score else 0
                exam = score.exam if score else 0

                total = t1 + t2 + t3 + exam
                student_total += total

                subject_results.append({
                    "subject_id": subject.id,
                    "subject_name": subject.name,
                    "test1": t1,
                    "test2": t2,
                    "test3": t3,
                    "exam": exam,
                    "total": total
                })

            totals.append({"student_id": student.id, "total": student_total})

            students_data.append({
                "id": student.id,
                "name": student.name,
                "class_number": student.class_number,
                "subjects": subject_results,
                "total": student_total  # Add total to student
            })

        # Calculate positions based on total (descending)
        sorted_totals = sorted(totals, key=lambda x: x["total"], reverse=True)
        position_map = {}
        current_position = 1
        last_total = None
        for idx, entry in enumerate(sorted_totals):
            if last_total is not None and entry["total"] == last_total:
                # same total as previous student → same position
                position_map[entry["student_id"]] = current_position
            else:
                current_position = idx + 1
                position_map[entry["student_id"]] = current_position
            last_total = entry["total"]

        # Add position to students_data
        for student in students_data:
            student["position"] = position_map.get(student["id"], None)

        return {
            "class_id": class_obj.id,
            "class_name": class_obj.name,
            "subjects": [{"id": s.id, "name": s.name} for s in subjects],
            "students": students_data
        }
    
    def get_class_result(self, db: Session, class_id: int):

        # Get class
        class_obj = (
            db.query(Class)
            .filter(Class.id == class_id)
            .first()
        )

        if not class_obj:
            return None

        # Get students in class
        students = (
            db.query(Student)
            .filter(Student.class_id == class_id)
            .all()
        )

        # Get subjects assigned to class
        subjects = (
            db.query(Subject)
            .join(ClassSubject, ClassSubject.subject_id == Subject.id)
            .filter(ClassSubject.class_id == class_id)
            .all()
        )

        student_ids = [s.id for s in students]
        subject_ids = [s.id for s in subjects]

        # Get scores only for this class students + subjects
        scores = []
        if student_ids and subject_ids:
            scores = (
                db.query(Score)
                .filter(
                    Score.student_id.in_(student_ids),
                    Score.subject_id.in_(subject_ids)
                )
                .all()
            )

        # Create quick lookup map
        score_map = {
            (score.student_id, score.subject_id): score
            for score in scores
        }

        # Build response
        students_data = []

        for student in students:

            subject_results = []

            for subject in subjects:
                score = score_map.get((student.id, subject.id))

                subject_results.append({
                    "subject_id": subject.id,
                    "subject_name": subject.name,
                    "test1": score.test1 if score else None,
                    "test2": score.test2 if score else None,
                    "test3": score.test3 if score else None,
                    "exam": score.exam if score else None
                })

            students_data.append({
                "id": student.id,
                "name": student.name,
                "class_number": student.class_number,
                "subjects": subject_results
            })

        return {
            "class_id": class_obj.id,
            "class_name": class_obj.name,
            "subjects": [
                {
                    "id": s.id,
                    "name": s.name
                } for s in subjects
            ],
            "students": students_data
        }

    def fetch(self):
        pass
    
    def fetch_all(self):
        pass

    def update(self):
        pass

    
    def delete(self):
        pass

score_service = ScoreService()




