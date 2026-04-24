from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.students import Student
from app.schemas.students import StudentCreateSchema
from app.services.classes import class_service


class StudentService:
    def create(self, db: Session, schema: StudentCreateSchema):
        class_obj = class_service.get_by_id(db, schema.class_id)
        duplicate_roll = (
            db.query(Student)
            .filter(Student.class_id == schema.class_id, Student.class_number == schema.class_number)
            .first()
        )
        if duplicate_roll:
            raise HTTPException(status_code=409, detail="A student already uses this class number")

        create_student = Student(
            name=schema.name.strip(),
            class_id=class_obj.id,
            class_number=schema.class_number,
            admission_number=schema.admission_number.strip() if schema.admission_number else None,
            gender=schema.gender.strip() if schema.gender else None,
        )
        db.add(create_student)
        db.commit()
        db.refresh(create_student)
        return create_student

    def fetch_by_class_id(self, db: Session, class_id: int):
        students = (
            db.query(Student)
            .filter(Student.class_id == class_id)
            .order_by(Student.class_number.asc(), Student.name.asc())
            .all()
        )
        return students

student_service = StudentService()
