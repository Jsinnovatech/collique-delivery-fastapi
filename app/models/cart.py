from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column, Relationship, ForeignKey, UniqueConstraint
from sqlalchemy import DateTime, func


class CartItemBase(SQLModel):
    quantity: int = Field(default=1, ge=1)


class CartItem(CartItemBase, table=True):
    __tablename__ = "cart_items"
    __table_args__ = (UniqueConstraint("user_id", "product_id"),)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    store_id: UUID = Field(foreign_key="stores.id")
    product_id: UUID = Field(foreign_key="products.id")

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
    user: "User" = Relationship(back_populates="cart_items")
    product: "Product" = Relationship(back_populates="cart_items")


class CartItemCreate(CartItemBase):
    product_id: UUID


class CartItemUpdate(SQLModel):
    quantity: int = Field(ge=1)


class CartItemResponse(CartItemBase):
    id: UUID
    user_id: UUID
    store_id: UUID
    product_id: UUID
    created_at: datetime
    updated_at: datetime


class CartItemWithProduct(CartItemResponse):
    product: "ProductResponse"