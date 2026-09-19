from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Contact(Base):
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
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    avatar: Mapped[str | None] = mapped_column(String(500), nullable=True)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    contacts: Mapped[list[Contact]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
