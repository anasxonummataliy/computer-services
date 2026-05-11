from datetime import datetime
import secrets
from typing import Optional, Tuple
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, Session
from app.database.base import Base
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    role: Mapped[str] = mapped_column(String(50), default="user")
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_by_email(cls, db: Session, email: str) -> Optional["Users"]:
        return db.query(cls).filter(cls.email == email).first()

    @classmethod
    def get_by_id(cls, db: Session, user_id: int) -> Optional["Users"]:
        return db.query(cls).filter(cls.id == user_id).first()

    @classmethod
    def create(cls, db: Session, user_data: dict) -> Tuple[int, Optional[str]]:
        random_password = None
        if not user_data.get("password"):
            random_password = str(secrets.randbelow(10**9))
            user_data["password"] = random_password

        hashed_pw = cls.hash_password(user_data["password"])

        new_user = cls(
            email=user_data["email"],
            password=hashed_pw,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user.id, random_password

    @classmethod
    def update(cls, db: Session, user_id: int, data: dict) -> None:
        db.query(cls).filter(cls.id == user_id).update(data)
        db.commit()

    @classmethod
    def delete(cls, db: Session, user_id: int) -> None:
        user = cls.get_by_id(db, user_id)
        if user:
            db.delete(user)
            db.commit()
