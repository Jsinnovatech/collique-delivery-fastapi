from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import DateTime, func


class AdminBase(SQLModel):
    name: str = Field(max_length=100)
    email: str = Field(unique=True, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: str = Field(default="superadmin", max_length=20)
    is_active: bool = Field(default=True)


class Admin(AdminBase, table=True):
    __tablename__ = "admins"

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


class AdminCreate(AdminBase):
    password: str = Field(min_length=6)


class AdminUpdate(SQLModel):
    name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class AdminResponse(AdminBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class AdminLogin(SQLModel):
    email: str
    password: str