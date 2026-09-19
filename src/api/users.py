import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, File, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.database.db import get_db
from src.database.models import User
from src.repository.users import UserRepository
from src.schemas import UserResponse
from src.services.auth import get_current_user


router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/me", response_model=UserResponse)
@limiter.limit("5/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    return user


@router.patch("/avatar", response_model=UserResponse)
async def update_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cloudinary.config(
        cloud_name=config.CLOUDINARY_CLOUD_NAME,
        api_key=config.CLOUDINARY_API_KEY,
        api_secret=config.CLOUDINARY_API_SECRET,
        secure=True,
    )
    result = await run_in_threadpool(
        cloudinary.uploader.upload,
        file.file,
        public_id=f"contacts_api/users/{user.id}",
        overwrite=True,
    )
    return await UserRepository(db).update_avatar(user, result["secure_url"])
