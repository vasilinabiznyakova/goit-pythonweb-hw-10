from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.database.db import get_db
from src.repository.users import UserRepository
from src.schemas import Token, UserCreate, UserResponse
from src.services.auth import create_token, decode_token, hash_password, verify_password
from src.services.email import send_verification_email


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    repository = UserRepository(db)
    if await repository.get_by_email(str(body.email)):
        raise HTTPException(status_code=409, detail="User with this email already exists")
    if await repository.get_by_username(body.username):
        raise HTTPException(status_code=409, detail="User with this username already exists")
    user = await repository.create(body, hash_password(body.password))
    token = create_token(user.email, "email", config.EMAIL_TOKEN_EXPIRATION_SECONDS)
    background_tasks.add_task(send_verification_email, user.email, token)
    return user


@router.post("/login", response_model=Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    user = await UserRepository(db).get_by_username(form.username)
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(status_code=401, detail="Email is not verified")
    token = create_token(user.username, "access", config.JWT_EXPIRATION_SECONDS)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = decode_token(token, "email")
    repository = UserRepository(db)
    user = await repository.get_by_email(email)
    if user is None:
        raise HTTPException(status_code=400, detail="Verification error")
    if not user.confirmed:
        await repository.confirm_email(user)
    return {"message": "Email confirmed"}
