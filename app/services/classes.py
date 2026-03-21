
from fastapi import Depends, HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.classes import Class
from app.schemas.classes import CreateSchema


class ClassService():
    """Class service"""
    
    def create(self, db: Session, schema: CreateSchema):
        class_create = Class(name=schema.name)
        db.add(class_create)
        db.commit()
        db.refresh(class_create)
        return class_create

    def fetch(self):
        pass
    
    def fetch_all(self, db: Session):
        classes = db.query(Class).all()
        return classes

    def update(self):
        pass

    
    def delete(self):
        pass

class_service = ClassService()




