from datetime import date, timedelta
from typing import List

from sqlalchemy import extract, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdate


class ContactRepository:
    """Data-access layer for contacts owned by a specific user."""

    def __init__(self, session: AsyncSession):
        """Initialize the repository with an asynchronous session."""
        self.db = session

    async def get_contacts(
        self,
        skip: int,
        limit: int,
        user: User,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
    ) -> List[Contact]:
        """List a user's contacts with pagination and optional search filters."""
        stmt = select(Contact).where(Contact.user_id == user.id)
        filters = []

        if first_name:
            filters.append(Contact.first_name.ilike(f"%{first_name}%"))
        if last_name:
            filters.append(Contact.last_name.ilike(f"%{last_name}%"))
        if email:
            filters.append(Contact.email.ilike(f"%{email}%"))
        if filters:
            stmt = stmt.where(or_(*filters))

        stmt = stmt.order_by(Contact.id).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return list(contacts.scalars().all())

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """Return one contact when it belongs to the supplied user."""
        stmt = select(Contact).filter_by(id=contact_id, user_id=user.id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def get_contact_by_email(self, email: str, user: User) -> Contact | None:
        """Find a user's contact by exact email address."""
        stmt = select(Contact).filter_by(email=email, user_id=user.id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """Create and persist a contact owned by a user."""
        contact = Contact(**body.model_dump(), user_id=user.id)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdate, user: User
    ) -> Contact | None:
        """Apply supplied fields to an existing contact."""
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """Delete a contact when it exists and belongs to the user."""
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def get_upcoming_birthdays(self, user: User, days: int = 7) -> List[Contact]:
        """Return contacts whose birthdays occur in the next ``days`` days."""
        today = date.today()
        dates = [today + timedelta(days=offset) for offset in range(days)]
        conditions = [
            (extract("month", Contact.birthday) == day.month)
            & (extract("day", Contact.birthday) == day.day)
            for day in dates
        ]

        contacts = await self.db.execute(
            select(Contact)
            .where(Contact.user_id == user.id, or_(*conditions))
            .order_by(Contact.id)
        )
        return list(contacts.scalars().all())
