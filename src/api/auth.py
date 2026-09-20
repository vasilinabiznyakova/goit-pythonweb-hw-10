from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.database.db import get_db
from src.repository.users import UserRepository
from src.schemas import PasswordReset, PasswordResetRequest, Token, UserCreate, UserResponse
from src.services.auth import create_token, decode_token, hash_password, verify_password
from src.services.cache import cache_user, delete_cached_user
from src.services.email import send_password_reset_email, send_verification_email


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Register a user and enqueue an email-confirmation message."""
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
    """Authenticate a confirmed user and issue an access token."""
    user = await UserRepository(db).get_by_username(form.username)
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(status_code=401, detail="Email is not verified")
    await cache_user(user)
    token = create_token(user.username, "access", config.JWT_EXPIRATION_SECONDS)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """Confirm an email address using a signed email token."""
    email = decode_token(token, "email")
    repository = UserRepository(db)
    user = await repository.get_by_email(email)
    if user is None:
        raise HTTPException(status_code=400, detail="Verification error")
    if not user.confirmed:
        await repository.confirm_email(user)
    return {"message": "Email confirmed"}


@router.post("/request-password-reset", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    body: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Send a reset message when the account exists without exposing its presence."""
    user = await UserRepository(db).get_by_email(str(body.email))
    if user is not None:
        token = create_token(
            user.email,
            "password_reset",
            config.PASSWORD_RESET_TOKEN_EXPIRATION_SECONDS,
        )
        background_tasks.add_task(send_password_reset_email, user.email, token)
    return {"message": "If the account exists, a reset email has been sent"}


@router.post("/reset-password")
async def reset_password(body: PasswordReset, db: AsyncSession = Depends(get_db)):
    """Replace the password after validating a short-lived, single-purpose JWT."""
    email = decode_token(body.token, "password_reset")
    repository = UserRepository(db)
    user = await repository.get_by_email(email)
    if user is None:
        raise HTTPException(status_code=400, detail="Password reset error")
    await repository.update_password(user, hash_password(body.new_password))
    await delete_cached_user(user.username)
    return {"message": "Password has been reset"}
