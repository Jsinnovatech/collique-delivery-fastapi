from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column, Relationship, ForeignKey
from sqlalchemy import DateTime, func


class ProductBase(SQLModel):
    name: str = Field(max_length=100)
    description: Optional[str] = None
    image: Optional[str] = Field(None, max_length=500)
    price: Decimal = Field(decimal_places=2, max_digits=10)
    original_price: Optional[Decimal] = Field(None, decimal_places=2, max_digits=10)
    discount: Decimal = Field(default=Decimal("0"), decimal_places=2, max_digits=5)

    stock: int = Field(default=0)
    unit: str = Field(default="unidad", max_length=20)

    is_available: bool = Field(default=True)
    is_featured: bool = Field(default=False)


class Product(ProductBase, table=True):
    __tablename__ = "products"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    store_id: UUID = Field(foreign_key="stores.id")
    category_id: Optional[UUID] = Field(None, foreign_key="categories.id")

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
    store: "Store" = Relationship(back_populates="products")
    category: "Category" = Relationship(back_populates="products")
    order_items: List["OrderItem"] = Relationship(back_populates="product")
    cart_items: List["CartItem"] = Relationship(back_populates="product")


class ProductCreate(ProductBase):
    store_id: UUID
    category_id: UUID


class ProductUpdate(SQLModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    image: Optional[str] = Field(None, max_length=500)
    price: Optional[Decimal] = Field(None, decimal_places=2, max_digits=10)
    original_price: Optional[Decimal] = Field(None, decimal_places=2, max_digits=10)
    discount: Optional[Decimal] = Field(None, decimal_places=2, max_digits=5)
    stock: Optional[int] = None
    unit: Optional[str] = Field(None, max_length=20)
    category_id: Optional[UUID] = None
    is_available: Optional[bool] = None
    is_featured: Optional[bool] = None


class ProductResponse(ProductBase):
    id: UUID
    store_id: UUID
    category_id: UUID
    created_at: datetime
    updated_at: datetime


class ProductWithStore(ProductResponse):
    store: "StorePublic"
    category: "CategoryResponse"