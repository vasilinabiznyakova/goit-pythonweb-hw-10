"""Unit tests for repository behavior with mocked async sessions."""

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.repository.users import UserRepository
from src.schemas import ContactModel, ContactUpdate, UserCreate


@pytest.fixture
def session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def user():
    return User(id=1, username="test", email="test@example.com", hashed_password="hash")


@pytest.mark.asyncio
async def test_contact_repository_crud(session, user):
    repository = ContactRepository(session)
    body = ContactModel(
        first_name="Ada", last_name="Lovelace", email="ada@example.com",
        phone="1234567", birthday=date(1815, 12, 10)
    )
    created = await repository.create_contact(body, user)
    assert created.email == "ada@example.com"
    session.add.assert_called_once_with(created)
    session.commit.assert_awaited_once()

    existing = Contact(id=1, user_id=1, **body.model_dump())
    repository.get_contact_by_id = AsyncMock(return_value=existing)
    session.reset_mock()
    updated = await repository.update_contact(1, ContactUpdate(first_name="Augusta"), user)
    assert updated.first_name == "Augusta"
    session.commit.assert_awaited_once()

    session.reset_mock()
    removed = await repository.remove_contact(1, user)
    assert removed is existing
    session.delete.assert_awaited_once_with(existing)


@pytest.mark.asyncio
async def test_contact_repository_missing_update_and_delete(session, user):
    repository = ContactRepository(session)
    repository.get_contact_by_id = AsyncMock(return_value=None)
    assert await repository.update_contact(99, ContactUpdate(first_name="Nope"), user) is None
    assert await repository.remove_contact(99, user) is None
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_contact_repository_queries(session, user):
    contact = Contact(
        id=1, user_id=1, first_name="Ada", last_name="Lovelace",
        email="ada@example.com", phone="1234567", birthday=date(1815, 12, 10)
    )
    result = MagicMock()
    result.scalars.return_value.all.return_value = [contact]
    result.scalar_one_or_none.return_value = contact
    session.execute.return_value = result
    repository = ContactRepository(session)
    assert await repository.get_contacts(0, 10, user, "Ad", "Love", "example") == [contact]
    assert await repository.get_contact_by_id(1, user) is contact
    assert await repository.get_contact_by_email(contact.email, user) is contact
    assert await repository.get_upcoming_birthdays(user) == [contact]


@pytest.mark.asyncio
async def test_user_repository_all_mutations(session):
    repository = UserRepository(session)
    result = MagicMock()
    found = User(id=1, username="alice", email="alice@example.com", hashed_password="old")
    result.scalar_one_or_none.return_value = found
    session.execute.return_value = result
    assert await repository.get_by_username("alice") is found
    assert await repository.get_by_email("alice@example.com") is found

    body = UserCreate(username="newuser", email="new@example.com", password="secret1")
    created = await repository.create(body, "hash")
    assert created.username == "newuser"
    await repository.confirm_email(created)
    assert created.confirmed is True
    assert (await repository.update_avatar(created, "https://avatar")) is created
    await repository.update_password(created, "new-hash")
    assert created.hashed_password == "new-hash"
