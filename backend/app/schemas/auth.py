from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal


class UserRegister(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    password: str
    person_type: Literal["individual", "legal"]
    company_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    person_type: str
    company_name: Optional[str]
