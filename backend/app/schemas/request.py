from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional, Literal


class SupportRequestCreate(BaseModel):
    device_model: str
    issue_type: Literal["hardware", "software", "network", "other"]
    problem_area: str
    description: str
    location: str
    status: Literal[
        "pending", "checked", "approved", "in_progress", "rejected", "completed"
    ] = "pending"


class SupportRequestUpdate(BaseModel):
    status: Literal[
        "pending", "checked", "approved", "in_progress", "rejected", "completed"
    ]
    master_id: Optional[str]


class SupportRequestResponse(BaseModel):
    device_model: str
    issue_type: Literal["hardware", "software", "network", "other"]
    problem_area: str
    description: str
    location: str
    status: Literal[
        "pending", "checked", "approved", "in_progress", "rejected", "completed"
    ]
    master: Optional[str]
    owner: Optional[str]


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str


class SupportRequestWithUserCreate(BaseModel):
    request: SupportRequestCreate
    user: UserCreate


class SupportRequestEdited(BaseModel):
    component_id: str
    quantity: int
    price: float
    end_date: datetime
