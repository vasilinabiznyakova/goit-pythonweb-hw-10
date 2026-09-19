from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactModel, ContactResponse, ContactUpdate
from src.services.contacts import ContactService
from src.services.auth import get_current_user


router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    first_name: str | None = Query(default=None),
    last_name: str | None = Query(default=None),
    email: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    return await contact_service.get_contacts(
        skip, limit, user, first_name, last_name, email
    )


@router.get("/birthdays", response_model=List[ContactResponse])
async def read_upcoming_birthdays(
    db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)
):
    contact_service = ContactService(db)
    return await contact_service.get_upcoming_birthdays(user)


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    contact = await contact_service.get_contact_by_email(body.email, user)
    if contact:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact with this email already exists",
        )
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactUpdate,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    if body.email and body.email != contact.email:
        existing_contact = await contact_service.get_contact_by_email(body.email, user)
        if existing_contact:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Contact with this email already exists",
            )
    contact = await contact_service.update_contact(contact_id, body, user)
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
