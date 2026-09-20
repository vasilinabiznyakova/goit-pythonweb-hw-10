from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas import ContactModel, ContactUpdate
from src.database.models import User


class ContactService:
    """Application service coordinating contact operations."""

    def __init__(self, db: AsyncSession):
        """Initialize the service for a database session."""
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactModel, user: User):
        """Create a contact for the authenticated user."""
        return await self.repository.create_contact(body, user)

    async def get_contacts(
        self,
        skip: int,
        limit: int,
        user: User,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
    ):
        """List and optionally search the authenticated user's contacts."""
        return await self.repository.get_contacts(
            skip, limit, user, first_name, last_name, email
        )

    async def get_contact(self, contact_id: int, user: User):
        """Return a contact by identifier."""
        return await self.repository.get_contact_by_id(contact_id, user)

    async def get_contact_by_email(self, email: str, user: User):
        """Return a contact by email."""
        return await self.repository.get_contact_by_email(email, user)

    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User):
        """Update an existing contact."""
        return await self.repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        """Remove an existing contact."""
        return await self.repository.remove_contact(contact_id, user)

    async def get_upcoming_birthdays(self, user: User):
        """List contacts with birthdays during the next seven days."""
        return await self.repository.get_upcoming_birthdays(user)
