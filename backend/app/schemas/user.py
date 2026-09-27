"""
사용자 Pydantic 스키마
"""
import json
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from typing import Optional, List, Literal


def require_nonblank(value: str) -> str:
    """Validate without changing the supplied string, including passwords."""
    if not value.strip():
        raise ValueError("must not be empty or whitespace-only")
    return value

class UserBase(BaseModel):
    username: str
    email: str
    weight_kg: Optional[float] = None
    height_cm: Optional[int] = None
    foot_size: Optional[str] = None
    foot_width: Optional[str] = None
    arch_type: Optional[str] = None
    running_style: Optional[str] = None
    budget_won: Optional[int] = None
    preferred_brands: Optional[List[str]] = None

    @field_validator("username", "email")
    @classmethod
    def validate_identity(cls, value: str) -> str:
        return require_nonblank(value)

class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return require_nonblank(value)

class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    weight_kg: Optional[float] = None
    height_cm: Optional[int] = None
    foot_size: Optional[str] = None
    foot_width: Optional[str] = None
    arch_type: Optional[str] = None
    running_style: Optional[str] = None
    budget_won: Optional[int] = None
    preferred_brands: Optional[List[str]] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("preferred_brands", mode="before")
    @classmethod
    def deserialize_brands(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        return value

class UserLogin(BaseModel):
    username: str
    password: str

    @field_validator("username", "password")
    @classmethod
    def validate_credentials(cls, value: str) -> str:
        return require_nonblank(value)

class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(gt=0, description="Access token lifetime in seconds")

    @field_validator("access_token")
    @classmethod
    def validate_access_token(cls, value: str) -> str:
        return require_nonblank(value)
