from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.classes import Class
from app.models.scores import Score
from app.models.students import Student
from app.models.subjects import ClassSubject, Subject
from app.models.users import User
from app.schemas.scores import scoreSchema
from app.services.classes import class_service


class ScoreService:
    @staticmethod
    def grade_from_score(score: float) -> str:
        if score >= 75:
            return "A"
        if score >= 65:
            return "B"
        if score >= 55:
            return "C"
        if score >= 45:
            return "D"
        if score >= 40:
            return "E"
        return "F"

    @staticmethod
    def remark_from_score(score: float) -> str:
        if score >= 75:
            return "Excellent"
        if score >= 65:
            return "Very Good"
        if score >= 55:
            return "Good"
        if score >= 45:
            return "Fair"
        if score >= 40:
            return "Pass"
        return "Needs Support"

    def _get_class_subjects(self, db: Session, class_id: int):
        return (
            db.query(ClassSubject)
            .join(Subject, Subject.id == ClassSubject.subject_id)
            .filter(ClassSubject.class_id == class_id)
            .order_by(Subject.name.asc())
            .all()
        )

    def _get_students(self, db: Session, class_id: int):
        return (
            db.query(Student)
            .filter(Student.class_id == class_id)
            .order_by(Student.class_number.asc(), Student.name.asc())
            .all()
        )

    def _score_map(self, db: Session, student_ids: list[int], subject_ids: list[int]):
        if not student_ids or not subject_ids:
            return {}
        scores = (
            db.query(Score)
            .filter(Score.student_id.in_(student_ids), Score.subject_id.in_(subject_ids))
            .all()
        )
        return {(score.student_id, score.subject_id): score for score in scores}

    def add_update_score(self, db: Session, schema: scoreSchema, current_user: User):
        student = db.query(Student).filter(Student.id == schema.student_id).first()
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

        assignment = (
            db.query(ClassSubject)
            .filter(
                ClassSubject.class_id == student.class_id,
                ClassSubject.subject_id == schema.subject_id,
            )
            .first()
        )
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject is not assigned to this student's class",
            )

        if not class_service.can_edit_subject_scores(
            current_user=current_user,
            class_id=student.class_id,
            subject_id=schema.subject_id,
            db=db,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to edit this subject",
            )

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
            score = Score(
                student_id=schema.student_id,
                subject_id=schema.subject_id,
                test1=schema.test1 or 0,
                test2=schema.test2 or 0,
                test3=schema.test3 or 0,
                exam=schema.exam or 0,
            )
            db.add(score)
        db.commit()
        db.refresh(score)
        return {
            "student_id": score.student_id,
            "subject_id": score.subject_id,
            "test1": score.test1,
            "test2": score.test2,
            "test3": score.test3,
            "exam": score.exam,
            "total": score.test1 + score.test2 + score.test3 + score.exam,
        }

    def build_class_dataset(self, db: Session, class_id: int):
        class_obj = db.query(Class).filter(Class.id == class_id).first()
        if not class_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")

        subject_links = self._get_class_subjects(db, class_id)
        students = self._get_students(db, class_id)
        subject_ids = [link.subject_id for link in subject_links]
        student_ids = [student.id for student in students]
        score_map = self._score_map(db, student_ids, subject_ids)

        students_data = []
        totals = []
        for student in students:
            subject_rows = []
            student_total = 0.0

            for link in subject_links:
                score = score_map.get((student.id, link.subject_id))
                test1 = score.test1 if score else 0.0
                test2 = score.test2 if score else 0.0
                test3 = score.test3 if score else 0.0
                exam = score.exam if score else 0.0
                total = test1 + test2 + test3 + exam
                student_total += total

                subject_rows.append(
                    {
                        "subject_id": link.subject_id,
                        "subject_name": link.subject.name,
                        "teacher_id": link.teacher_id,
                        "teacher_name": link.teacher.full_name if link.teacher else None,
                        "test1": test1,
                        "test2": test2,
                        "test3": test3,
                        "exam": exam,
                        "total": total,
                        "average": round(total / 4, 2),
                        "grade": self.grade_from_score(total),
                        "remark": self.remark_from_score(total),
                    }
                )

            totals.append({"student_id": student.id, "total": student_total})
            students_data.append(
                {
                    "id": student.id,
                    "name": student.name,
                    "class_number": student.class_number,
                    "admission_number": student.admission_number,
                    "gender": student.gender,
                    "subjects": subject_rows,
                    "total": round(student_total, 2),
                    "average": round(student_total / len(subject_links), 2) if subject_links else 0,
                }
            )

        sorted_totals = sorted(totals, key=lambda item: item["total"], reverse=True)
        position_map = {}
        current_position = 0
        last_total = None
        for index, item in enumerate(sorted_totals, start=1):
            if last_total != item["total"]:
                current_position = index
            position_map[item["student_id"]] = current_position
            last_total = item["total"]

        for student in students_data:
            student["position"] = position_map.get(student["id"])

        return {
            "class_id": class_obj.id,
            "class_name": class_obj.name,
            "form_teacher_id": class_obj.form_teacher_id,
            "form_teacher_name": class_obj.form_teacher.full_name if class_obj.form_teacher else None,
            "subjects": [
                {
                    "id": link.subject_id,
                    "name": link.subject.name,
                    "teacher_id": link.teacher_id,
                    "teacher_name": link.teacher.full_name if link.teacher else None,
                }
                for link in subject_links
            ],
            "students": students_data,
            "student_count": len(students_data),
        }

    def get_score_entry(self, db: Session, class_id: int, current_user: User):
        class_service.get_by_id(db, class_id)
        data = self.build_class_dataset(db, class_id)

        if current_user.is_admin:
            allowed_subject_ids = {subject["id"] for subject in data["subjects"]}
        else:
            allowed_subject_ids = {
                subject["id"]
                for subject in data["subjects"]
                if subject["teacher_id"] == current_user.id
            }

        if not allowed_subject_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not assigned to edit any subject in this class",
            )

        data["subjects"] = [subject for subject in data["subjects"] if subject["id"] in allowed_subject_ids]
        for student in data["students"]:
            student["subjects"] = [
                subject for subject in student["subjects"] if subject["subject_id"] in allowed_subject_ids
            ]
        return data

    def get_class_results(self, db: Session, class_id: int, current_user: User):
        class_obj = class_service.get_by_id(db, class_id)
        if not class_service.can_view_class_results(current_user, class_obj):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the assigned form teacher or an administrator can view class results",
            )
        return self.build_class_dataset(db, class_id)

    def get_student_score(self, db: Session, student_id: int, current_user: User):
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

        class_obj = class_service.get_by_id(db, student.class_id)
        if not class_service.can_view_class_results(current_user, class_obj):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the assigned form teacher or an administrator can view result sheets",
            )

        class_data = self.build_class_dataset(db, student.class_id)
        student_result = next((item for item in class_data["students"] if item["id"] == student_id), None)
        if not student_result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student result not found")

        return {
            "student_info": {
                "id": student_result["id"],
                "name": student_result["name"],
                "class_id": student.class_id,
                "class_name": class_data["class_name"],
                "class_number": student_result["class_number"],
                "admission_number": student_result["admission_number"],
                "gender": student_result["gender"],
            },
            "subjects": student_result["subjects"],
            "number_of_subjects": len(student_result["subjects"]),
            "overall_total": student_result["total"],
            "overall_average": student_result["average"],
            "position": student_result["position"],
            "form_teacher_name": class_data["form_teacher_name"],
            "student_count": class_data["student_count"],
        }

score_service = ScoreService()
