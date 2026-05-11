from typing import List
from sqlalchemy import String, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, Session
from app.database.base import Base
from fastapi import HTTPException


class Components(Base):
    __tablename__ = "components"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=True)
    in_stock: Mapped[int] = mapped_column(Integer, default=0)

    details: Mapped[dict] = mapped_column(JSON, nullable=True)

    @classmethod
    def create(cls, db: Session, data: dict):
        new_component = cls(**data)
        db.add(new_component)
        db.commit()
        db.refresh(new_component)
        return {"id": new_component.id}

    @classmethod
    def get_by_id(cls, db: Session, component_id: int):
        # ObjectId validatsiyasi shart emas, FastAPI int ekanini tekshiradi
        doc = db.query(cls).filter(cls.id == component_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Component not found")
        return doc

    @classmethod
    def list(cls, db: Session, filters: dict = {}) -> List["Components"]:
        query = db.query(cls)
        if filters:
            query = query.filter_by(**filters)
        return query.all()

    @classmethod
    def update(cls, db: Session, component_id: int, data: dict):
        db_comp = db.query(cls).filter(cls.id == component_id).first()
        if not db_comp:
            raise HTTPException(status_code=404, detail="Component not found")

        for key, value in data.items():
            if hasattr(db_comp, key):
                setattr(db_comp, key, value)

        db.commit()
        return {"modified_count": 1}

    @classmethod
    def delete(cls, db: Session, component_id: int):
        db_comp = db.query(cls).filter(cls.id == component_id).first()
        if not db_comp:
            raise HTTPException(status_code=404, detail="Component not found")

        db.delete(db_comp)
        db.commit()
        return {"deleted_count": 1}
