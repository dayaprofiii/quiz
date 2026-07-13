import re

from pydantic import BaseModel, Field, field_validator


EMAIL_PATTERN = re.compile(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,63}$', re.IGNORECASE)


def normalize_email(value: str) -> str:
    email = value.strip().lower()
    if not EMAIL_PATTERN.fullmatch(email):
        raise ValueError('Введите корректную электронную почту.')
    return email


class AuthPayload(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1)

    @field_validator('email')
    @classmethod
    def validate_email(cls, value: str) -> str:
        return normalize_email(value)


class RegisterPayload(AuthPayload):
    name: str = Field(min_length=1, max_length=120)


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    role: str = 'user'


class AuthResponse(BaseModel):
    user: UserOut


class UserUpdatePayload(BaseModel):
    email: str | None = Field(default=None, min_length=3, max_length=320)
    name: str | None = Field(default=None, min_length=1, max_length=120)
    currentPassword: str | None = None
    nextPassword: str | None = None

    @field_validator('email')
    @classmethod
    def validate_optional_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_email(value)
