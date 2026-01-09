from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column, Relationship, ForeignKey
from sqlalchemy import DateTime, func


class AddressBase(SQLModel):
    label: str = Field(max_length=50)  # Casa, Trabajo, etc.
    address: str = Field(max_length=255)
    reference: Optional[str] = Field(None, max_length=255)
    latitude: Optional[Decimal] = Field(None, decimal_places=8, max_digits=10)
    longitude: Optional[Decimal] = Field(None, decimal_places=8, max_digits=11)
    is_default: bool = Field(default=False)
    is_active: bool = Field(default=True)


class Address(AddressBase, table=True):
    __tablename__ = "addresses"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    # Relationships
    user: "User" = Relationship(back_populates="addresses")


class AddressCreate(AddressBase):
    user_id: Optional[UUID] = None  # Will be set from auth


class AddressUpdate(SQLModel):
    label: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=255)
    reference: Optional[str] = Field(None, max_length=255)
    latitude: Optional[Decimal] = Field(None, decimal_places=8, max_digits=10)
    longitude: Optional[Decimal] = Field(None, decimal_places=8, max_digits=11)
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class AddressResponse(AddressBase):
    id: UUID
    user_id: UUID
    created_at: datetime