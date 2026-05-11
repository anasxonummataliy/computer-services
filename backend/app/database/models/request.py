from typing import List, Optional
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, Session, relationship
from app.database.base import Base
from fastapi import HTTPException


class SupportRequests(Base):
    __tablename__ = "support_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    device_model: Mapped[str] = mapped_column(String(255), nullable=True)
    issue_type: Mapped[str] = mapped_column(String(100), nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    owner = relationship("Users")

    @classmethod
    def create(cls, db: Session, data: dict):
        new_request = cls(**data)
        db.add(new_request)
        db.commit()
        db.refresh(new_request)
        return new_request

    @classmethod
    def get_by_id(cls, db: Session, req_id: int):
        doc = db.query(cls).filter(cls.id == req_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Support request not found")
        return doc

    @classmethod
    def get_by_owner_id(cls, db: Session, owner_id: int) -> List["SupportRequests"]:
        return db.query(cls).filter(cls.owner_id == owner_id).all()

    @classmethod
    def list(cls, db: Session, filters: dict = {}) -> List["SupportRequests"]:
        query = db.query(cls)
        if filters:
            query = query.filter_by(**filters)
        return query.all()

    @classmethod
    def update(cls, db: Session, req_id: int, data: dict):
        db_req = db.query(cls).filter(cls.id == req_id).first()
        if not db_req:
            raise HTTPException(status_code=404, detail="Support request not found")

        for key, value in data.items():
            setattr(db_req, key, value)

        db.commit()
        db.refresh(db_req)
        return {"modified": True}

    @classmethod
    def delete(cls, db: Session, req_id: int):
        db_req = db.query(cls).filter(cls.id == req_id).first()
        if not db_req:
            raise HTTPException(status_code=404, detail="Support request not found")

        db.delete(db_req)
        db.commit()
        return {"deleted": True}
