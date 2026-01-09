from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import DateTime, func


class UserBase(SQLModel):
    name: str = Field(max_length=100)
    email: str = Field(unique=True, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    profile_image: Optional[str] = Field(None, max_length=500)
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)


class User(UserBase, table=True):
    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password: str = Field(max_length=255)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now()
        )
    )

    # Relationships
    addresses: List["Address"] = Relationship(back_populates="user")
    orders: List["Order"] = Relationship(back_populates="user")
    cart_items: List["CartItem"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserUpdate(SQLModel):
    name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    profile_image: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class UserLogin(SQLModel):
    email: str
    password: str