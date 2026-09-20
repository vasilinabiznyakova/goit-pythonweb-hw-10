from datetime import date
from enum import Enum

from sqlalchemy import Boolean, Date, Enum as SqlEnum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy models."""

    pass


class UserRole(str, Enum):
    """Roles supported by the application authorization system."""

    USER = "user"
    ADMIN = "admin"


class Contact(Base):
    """A private contact belonging to one user account."""

    __tablename__ = "contacts"
    __table_args__ = (UniqueConstraint("email", "user_id", name="unique_contact_email_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    birthday: Mapped[date] = mapped_column(Date, nullable=False)
    additional_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="contacts")


class User(Base):
    """An authenticated account with a role and owned contacts."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    avatar: Mapped[str | None] = mapped_column(String(500), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole, name="user_role"), default=UserRole.USER, nullable=False
    )
    contacts: Mapped[list[Contact]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
