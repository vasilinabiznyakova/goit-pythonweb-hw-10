from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from src.database.models import UserRole


class ContactBase(BaseModel):
    """Fields shared by contact creation and response schemas."""

    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=5, max_length=30)
    birthday: date
    additional_data: str | None = Field(default=None, max_length=1000)


class ContactModel(ContactBase):
    """Payload used to create a contact."""

    pass


class ContactUpdate(BaseModel):
    """Optional fields accepted when partially updating a contact."""

    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=5, max_length=30)
    birthday: date | None = None
    additional_data: str | None = Field(default=None, max_length=1000)


class ContactResponse(ContactBase):
    """Public contact representation returned by the API."""

    id: int

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """Validated registration payload."""

    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)


class UserResponse(BaseModel):
    """Public user representation without a password hash."""

    id: int
    username: str
    email: EmailStr
    avatar: str | None
    confirmed: bool
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """OAuth2 bearer-token response."""

    access_token: str
    token_type: str


class PasswordResetRequest(BaseModel):
    """Request for a password-reset email."""

    email: EmailStr


class PasswordReset(BaseModel):
    """New password submitted together with a signed reset token."""

    token: str
    new_password: str = Field(min_length=6, max_length=72)
