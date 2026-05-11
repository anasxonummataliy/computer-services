from typing import Literal
from fastapi import FastAPI, HTTPException, Response, APIRouter, Depends, Body, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database.base import get_db, engine, Base
from app.database.models.user import Users
from app.database.models.request import SupportRequests
from app.database.models.components import Components

from app.schemas.components import ComponentsRequest, ComponentsUpdate
from app.schemas.request import (
    SupportRequestCreate,
    SupportRequestWithUserCreate,
    SupportRequestEdited,
)
from app.schemas.auth import UserRegister, UserLogin
from app.schemas.user import UserRequest, UserUpdate
from app.core.auth import create_access_token, create_refresh_token, verify_token
from app.utils.send_password import send_password

Base.metadata.create_all(bind=engine)

app = FastAPI(
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

api = APIRouter(prefix="/api")
oauth2_scheme = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    payload = verify_token(auth.credentials)
    if not payload:
        raise HTTPException(401, "Invalid token")
    user = Users.get_by_id(db, int(payload.get("sub")))
    if not user:
        raise HTTPException(404, "Foydalanuvchi topilmadi")
    return user


def manager_required(current_user: Users = Depends(get_current_user)):
    if current_user.role != "manager":
        raise HTTPException(403, "Ruxsat yo'q")
    return current_user


def master_or_manager_required(current_user: Users = Depends(get_current_user)):
    if current_user.role not in ["master", "manager"]:
        raise HTTPException(403, "Ruxsat yo'q")
    return current_user


@api.post("/register", summary="Ro'yxatdan o'tish")
def register(user: UserRegister, response: Response, db: Session = Depends(get_db)):
    if user.person_type == "legal" and not user.company_name:
        raise HTTPException(400, "Kompaniya nomini kiriting")
    if Users.get_by_email(db, user.email):
        raise HTTPException(400, "Bunday foydalanuvchi mavjud")

    data = user.model_dump()
    data["role"] = "user"
    user_id, _ = Users.create(db, data)

    payload = {"sub": str(user_id), "role": "user"}
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    response.set_cookie(
        "refresh_token", refresh_token, httponly=True, samesite="strict"
    )
    return {"access_token": access_token, "token_type": "bearer"}


@api.post("/login", summary="Login qilish")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    db_user = Users.get_by_email(db, user.email)
    if not db_user or not Users.verify_password(user.password, db_user.password):
        raise HTTPException(401, "Xato login yoki parol")

    payload = {"sub": str(db_user.id), "role": db_user.role}
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    response.set_cookie(
        "refresh_token", refresh_token, httponly=True, samesite="strict"
    )
    return {"access_token": access_token, "token_type": "bearer"}


@api.get("/me")
def me(current_user: Users = Depends(get_current_user)):
    return current_user


@api.get("/users", dependencies=[Depends(manager_required)])
def list_users(db: Session = Depends(get_db)):
    return db.query(Users).all()


@api.post("/support_request")
def create_request(
    request: SupportRequestCreate,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = request.model_dump()
    data["owner_id"] = current_user.id
    return SupportRequests.create(db, data)


@api.patch("/users/{user_id}", dependencies=[Depends(manager_required)])
def update_user(user_id: int, data_in: UserUpdate, db: Session = Depends(get_db)):
    existing_user = Users.get_by_id(db, user_id)
    if not existing_user:
        raise HTTPException(404, "Foydalanuvchi topilmadi")

    Users.update(db, user_id, data_in.model_dump(exclude_unset=True))
    return {"message": "User updated successfully"}


@api.delete("/users/{user_id}", dependencies=[Depends(manager_required)])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    Users.delete(db, user_id)
    return {"message": "User deleted successfully"}


@api.post(
    "/support_request_with_user", summary="Support request va user yaratish birga"
)
def create_request_with_user(
    data_in: SupportRequestWithUserCreate, db: Session = Depends(get_db)
):
    request_data = data_in.request.model_dump()
    user_data = data_in.user.model_dump()

    if Users.get_by_email(db, user_data["email"]):
        raise HTTPException(409, "Bunday foydalanuvchi mavjud")

    full_name = user_data.pop("full_name", "")
    parts = full_name.split(" ", 1)
    user_data["first_name"] = parts[0]
    user_data["last_name"] = parts[1] if len(parts) > 1 else ""
    user_data["role"] = "user"

    user_id, random_password = Users.create(db, user_data)

    request_data["owner_id"] = user_id
    SupportRequests.create(db, request_data)

    send_password(user_data["email"], random_password)

    return {"user_id": user_id}


@api.get("/support_request", summary="Support requestlarni ro'yxatini olish")
def list_requests(
    current_user: Users = Depends(get_current_user), db: Session = Depends(get_db)
):
    filters = {}
    if current_user.role == "manager":
        filters = {}
    elif current_user.role == "user":
        filters = {"owner_id": current_user.id}
    elif current_user.role == "master":
        filters = {"master_id": current_user.id}
    else:
        raise HTTPException(403, "Ruxsat yo'q")

    return SupportRequests.list(db, filters)


@api.put("/support_request/status/{request_id}")
def update_support_status(
    request_id: int,
    status: Literal[
        "checked", "approved", "in_progress", "rejected", "completed"
    ] = Body(...),
    db: Session = Depends(get_db),
):
    return SupportRequests.update(db, request_id, {"status": status})


@api.post("/support_request/send_master/{request_id}")
def send_support_master(
    request_id: int,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "manager":
        raise HTTPException(403, "Ruxsat yo'q")

    master = db.query(Users).filter(Users.role == "master").first()
    if not master:
        raise HTTPException(404, "Master topilmadi")

    SupportRequests.update(
        db, request_id, {"master_id": master.id, "status": "checked"}
    )
    return {"message": "Master assigned successfully"}


@api.patch("/support_request/master/{request_id}")
def update_support_master(
    request_id: int,
    data_in: SupportRequestEdited,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "master":
        raise HTTPException(403, "Ruxsat yo'q")

    db_component = Components.get_by_id(db, data_in.component_id)
    if not db_component:
        raise HTTPException(404, "Extiyot qism topilmadi")

    if db_component.in_stock < data_in.quantity:
        raise HTTPException(400, "Extiyot qism yetarli emas")

    remaining_quantity = db_component.in_stock - data_in.quantity
    Components.update(db, data_in.component_id, {"in_stock": remaining_quantity})

    return SupportRequests.update(
        db,
        request_id,
        {"end_date": data_in.end_date, "price": data_in.price, "status": "approved"},
    )


@api.post("/components", dependencies=[Depends(master_or_manager_required)])
def create_component(data_in: ComponentsRequest, db: Session = Depends(get_db)):
    return Components.create(db, data_in.model_dump())


@api.get(
    "/components/{component_id}", dependencies=[Depends(master_or_manager_required)]
)
def get_component(component_id: int, db: Session = Depends(get_db)):
    return Components.get_by_id(db, component_id)


@api.get("/components", dependencies=[Depends(master_or_manager_required)])
def list_components(db: Session = Depends(get_db)):
    return Components.list(db)


@api.patch(
    "/components/{component_id}", dependencies=[Depends(master_or_manager_required)]
)
def update_component(
    component_id: int, data_in: ComponentsUpdate, db: Session = Depends(get_db)
):
    return Components.update(db, component_id, data_in.model_dump(exclude_unset=True))


@api.delete(
    "/components/{component_id}", dependencies=[Depends(master_or_manager_required)]
)
def delete_component(component_id: int, db: Session = Depends(get_db)):
    Components.delete(db, component_id)
    return {"message": "Extiyot qism o'chirildi"}


@api.post("/create_default_users")
def create_default_users(db: Session = Depends(get_db)):
    manager = Users.get_by_email(db, "manager@gmail.com")
    if manager:
        Users.update(db, manager.id, {"role": "manager"})
    else:
        Users.create(
            db,
            {
                "email": "manager@gmail.com",
                "password": "manager",
                "first_name": "Admin",
                "last_name": "Manager",
                "role": "manager",
                "phone": "123",
                "person_type": "individual",
            },
        )

    master = Users.get_by_email(db, "master@gmail.com")
    if master:
        Users.update(db, master.id, {"role": "master"})
    else:
        Users.create(
            db,
            {
                "email": "master@gmail.com",
                "password": "master",
                "first_name": "Usta",
                "last_name": "Master",
                "role": "master",
                "phone": "456",
                "person_type": "individual",
            },
        )

    return {"message": "Rollari muvaffaqiyatli yangilandi!"}


app.include_router(api)
