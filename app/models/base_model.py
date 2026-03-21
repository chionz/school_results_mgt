#!/usr/bin/env python3
""" This is the Base Model Class
"""
from fastapi import Depends
from app.database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    func
)

class BaseTableModel(Base):
    """This model creates helper methods for all models"""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def to_dict(self):
        """returns a dictionary representation of the instance"""
        obj_dict = self.__dict__.copy()
        del obj_dict["_sa_instance_state"]
        obj_dict["id"] = self.id
        if self.created_at:
            obj_dict["created_at"] = self.created_at.isoformat()
        if self.updated_at:
            obj_dict["updated_at"] = self.updated_at.isoformat()
        return obj_dict

    @classmethod
    def get_all(cls):
        from app.database import get_db

        db = Depends(get_db)
        """ returns all instance of the class in the db
        """
        return db.query(cls).all()

    @classmethod
    def get_by_id(cls, id):
        from app.database import get_db

        db = Depends(get_db)
        """ returns a single object from the db
        """
        obj = db.query(cls).filter_by(id=id).first()
        return obj