from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=5, max_length=30)
    birthday: date
    additional_data: str | None = Field(default=None, max_length=1000)


class ContactModel(ContactBase):
    pass


class ContactUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=5, max_length=30)
    birthday: date | None = None
    additional_data: str | None = Field(default=None, max_length=1000)


class ContactResponse(ContactBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str | None
    confirmed: bool

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str
