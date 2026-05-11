from typing import Literal, Optional
from pydantic import BaseModel


class UserRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    password: str
    role: Literal["user", "manager", "master"] = "user"
    person_type: str
    company_name: Optional[str] = None


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    person_type: Optional[str] = None
    company_name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    role: str
    person_type: str
    company_name: str
