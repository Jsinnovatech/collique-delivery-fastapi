from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import DateTime, func


class CategoryBase(SQLModel):
    name: str = Field(max_length=50)
    icon: str = Field(default="📦", max_length=10)
    image: Optional[str] = Field(None, max_length=500)
    display_order: int = Field(default=0)
    is_active: bool = Field(default=True)


class Category(CategoryBase, table=True):
    __tablename__ = "categories"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )

    # Relationships
    products: List["Product"] = Relationship(back_populates="category")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(SQLModel):
    name: Optional[str] = Field(None, max_length=50)
    icon: Optional[str] = Field(None, max_length=10)
    image: Optional[str] = Field(None, max_length=500)
    display_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: UUID
    created_at: datetime