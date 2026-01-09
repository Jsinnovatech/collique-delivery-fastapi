from datetime import datetime, time
from typing import Optional, List
from decimal import Decimal
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import DateTime, func, Time


class StoreBase(SQLModel):
    owner_name: str = Field(max_length=100)
    owner_email: str = Field(unique=True, max_length=100)
    owner_phone: str = Field(max_length=20)

    # Store information
    store_name: str = Field(max_length=100)
    description: Optional[str] = None
    image: Optional[str] = Field(None, max_length=500)
    address: str = Field(max_length=255)
    latitude: Optional[Decimal] = Field(None, decimal_places=8, max_digits=10)
    longitude: Optional[Decimal] = Field(None, decimal_places=8, max_digits=11)

    # Configuration
    delivery_fee: Decimal = Field(default=Decimal("3.00"), decimal_places=2, max_digits=10)
    delivery_time_min: int = Field(default=20)
    delivery_time_max: int = Field(default=40)
    open_time: time = Field(default=time(8, 0))
    close_time: time = Field(default=time(22, 0))

    # Status
    rating: Decimal = Field(default=Decimal("0.0"), decimal_places=1, max_digits=2)
    total_reviews: int = Field(default=0)
    is_open: bool = Field(default=True)
    is_active: bool = Field(default=True)
    is_approved: bool = Field(default=False)


class Store(StoreBase, table=True):
    __tablename__ = "stores"

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
    products: List["Product"] = Relationship(back_populates="store")
    orders: List["Order"] = Relationship(back_populates="store")


class StoreCreate(StoreBase):
    password: str = Field(min_length=6)


class StoreUpdate(SQLModel):
    store_name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    image: Optional[str] = Field(None, max_length=500)
    address: Optional[str] = Field(None, max_length=255)
    latitude: Optional[Decimal] = Field(None, decimal_places=8, max_digits=10)
    longitude: Optional[Decimal] = Field(None, decimal_places=8, max_digits=11)
    delivery_fee: Optional[Decimal] = Field(None, decimal_places=2, max_digits=10)
    delivery_time_min: Optional[int] = None
    delivery_time_max: Optional[int] = None
    open_time: Optional[time] = None
    close_time: Optional[time] = None
    is_open: Optional[bool] = None
    is_approved: Optional[bool] = None


class StoreResponse(StoreBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class StoreLogin(SQLModel):
    email: str
    password: str


class StorePublic(SQLModel):
    id: UUID
    store_name: str
    description: Optional[str]
    image: Optional[str]
    address: str
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    delivery_fee: Decimal
    delivery_time_min: int
    delivery_time_max: int
    open_time: time
    close_time: time
    rating: Decimal
    total_reviews: int
    is_open: bool