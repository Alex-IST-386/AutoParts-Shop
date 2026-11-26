from fastapi import HTTPException, Depends, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import auth
import models
from database import SessionLocal
import schemas

from auth import get_current_user
from schemas import RegisterOut, RegisterIn, Token

router = APIRouter(tags = ["Пользователи"])

@router.post("/register", response_model = RegisterOut)
def register_user(user: RegisterIn, db: Session = Depends(auth.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code = 400, detail = "Пользователь с таким логином уже существует")

    hashed_password = auth.get_password_hash(user.password)

    ALLOWED_SELF_ROLES = ["user", "supplier"]
    if user.role not in ALLOWED_SELF_ROLES:
        raise HTTPException(status_code=403, detail="Эту роль может выдать только администратор")

    new_user = models.User(
        username = user.username,
        password_hash = hashed_password,
        role = user.role,
        avatar_url = user.avatar_url,
        email = user.email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model = Token)
def login_for_access_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(auth.get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Неверный логин или пароль",
            headers = {"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes = auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data = {"sub": user.username, "role": user.role},
        expires_delta = access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model = RegisterOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user

