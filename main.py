from fastapi import FastAPI, HTTPException
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional, List
import hashlib

app = FastAPI(title="CRUD Usuarios + Login")

sqlite_file_name = "database.db"
engine = create_engine(f"sqlite:///{sqlite_file_name}", echo=False)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    email: Optional[str] = None
    is_active: bool = True


class UserCreate(SQLModel):
    username: str
    password: str
    email: Optional[str] = None
    is_active: bool = True


class UserRead(SQLModel):
    id: int
    username: str
    email: Optional[str] = None
    is_active: bool


class UserUpdate(SQLModel):
    username: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class LoginRequest(SQLModel):
    username: str
    password: str


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_db():
    SQLModel.metadata.create_all(engine)


@app.on_event("startup")
def on_startup():
    create_db()


@app.post("/users", response_model=UserRead)
def create_user(user: UserCreate):
    with Session(engine) as session:
        existing_user = session.exec(
            select(User).where(User.username == user.username)
        ).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="El username ya existe")

        new_user = User(
            username=user.username,
            password_hash=hash_password(user.password),
            email=user.email,
            is_active=user.is_active
        )

        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user


@app.get("/users", response_model=List[UserRead])
def get_users():
    with Session(engine) as session:
        return session.exec(select(User)).all()


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no existe")
        return user


@app.put("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, updated: UserUpdate):
    with Session(engine) as session:
        user = session.get(User, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no existe")

        if updated.username is not None:
            other_user = session.exec(
                select(User).where(User.username == updated.username, User.id != user_id)
            ).first()
            if other_user:
                raise HTTPException(status_code=400, detail="Ese username ya está en uso")
            user.username = updated.username

        if updated.email is not None:
            user.email = updated.email

        if updated.is_active is not None:
            user.is_active = updated.is_active

        session.add(user)
        session.commit()
        session.refresh(user)
        return user


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="Usuario no existe")

        session.delete(user)
        session.commit()
        return {"mensaje": "Usuario eliminado correctamente"}


@app.post("/login")
def login(data: LoginRequest):
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.username == data.username)
        ).first()

        if not user:
            return {"mensaje": "Login fallido"}

        if not user.is_active:
            return {"mensaje": "Login fallido"}

        if user.password_hash == hash_password(data.password):
            return {"mensaje": "Login exitoso"}

        return {"mensaje": "Login fallido"}