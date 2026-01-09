from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from uuid import UUID, uuid4
from enum import Enum

from sqlmodel import SQLModel, Field, Column, Relationship, ForeignKey
from sqlalchemy import DateTime, func


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    ON_THE_WAY = "on_the_way"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    CASH = "cash"
    YAPE = "yape"
    PLIN = "plin"
    CARD = "card"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"


class OrderBase(SQLModel):
    order_number: str = Field(unique=True, max_length=20)

    # Delivery address snapshot
    delivery_address: str = Field(max_length=255)
    delivery_reference: Optional[str] = Field(None, max_length=255)
    delivery_latitude: Optional[Decimal] = Field(None, decimal_places=8, max_digits=10)
    delivery_longitude: Optional[Decimal] = Field(None, decimal_places=8, max_digits=11)

    # Totals
    subtotal: Decimal = Field(decimal_places=2, max_digits=10)
    delivery_fee: Decimal = Field(decimal_places=2, max_digits=10)
    discount_amount: Decimal = Field(default=Decimal("0"), decimal_places=2, max_digits=10)
    total: Decimal = Field(decimal_places=2, max_digits=10)

    # Payment
    payment_method: PaymentMethod
    payment_status: PaymentStatus = Field(default=PaymentStatus.PENDING)

    # Order status
    status: OrderStatus = Field(default=OrderStatus.PENDING)

    notes: Optional[str] = None

    # Status timestamps
    confirmed_at: Optional[datetime] = None
    preparing_at: Optional[datetime] = None
    on_the_way_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None


class Order(OrderBase, table=True):
    __tablename__ = "orders"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    store_id: UUID = Field(foreign_key="stores.id")
    address_id: Optional[UUID] = Field(None, foreign_key="addresses.id")

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
    user: "User" = Relationship(back_populates="orders")
    store: "Store" = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    order_id: UUID = Field(foreign_key="orders.id")
    product_id: UUID = Field(foreign_key="products.id")

    # Product snapshot
    product_name: str = Field(max_length=100)
    product_image: Optional[str] = Field(None, max_length=500)
    unit_price: Decimal = Field(decimal_places=2, max_digits=10)

    quantity: int
    total_price: Decimal = Field(decimal_places=2, max_digits=10)

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    # Relationships
    order: Order = Relationship(back_populates="items")
    product: "Product" = Relationship(back_populates="order_items")


class OrderItemCreate(SQLModel):
    product_id: UUID
    quantity: int


class OrderCreate(SQLModel):
    store_id: UUID
    items: List[OrderItemCreate]
    address_id: Optional[UUID] = None
    delivery_address: str
    delivery_reference: Optional[str] = None
    delivery_latitude: Optional[Decimal] = None
    delivery_longitude: Optional[Decimal] = None
    payment_method: PaymentMethod
    notes: Optional[str] = None


class OrderUpdate(SQLModel):
    status: Optional[OrderStatus] = None
    payment_status: Optional[PaymentStatus] = None
    cancellation_reason: Optional[str] = None


class OrderItemResponse(SQLModel):
    id: UUID
    product_id: UUID
    product_name: str
    product_image: Optional[str]
    unit_price: Decimal
    quantity: int
    total_price: Decimal


class OrderResponse(OrderBase):
    id: UUID
    user_id: UUID
    store_id: UUID
    address_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]