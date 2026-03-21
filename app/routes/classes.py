from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.classes import CreateSchema
from app.services.classes import class_service

# This maps and tags our users routes 
classrouter = APIRouter(prefix="/classes", tags=["Class"])

# This is an endpoint
@classrouter.post("/")
def create_class(schema: CreateSchema, db: Session = Depends(get_db)):
    db_class = class_service.create(db, schema=schema)
    return db_class

@classrouter.get("/list")
def all_class(db: Session = Depends(get_db)):
    all_class = class_service.fetch_all(db=db)
    return all_class