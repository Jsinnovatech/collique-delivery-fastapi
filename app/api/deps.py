from typing import Generator, Optional, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_session
from app.core.security import verify_token
from app.models import User, Store, Admin


security = HTTPBearer()


async def get_db() -> Generator[AsyncSession, None, None]:
    """Get database session dependency."""
    async for session in get_session():
        yield session


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> tuple[str, str]:
    """Get current user from JWT token."""
    token = credentials.credentials
    payload = verify_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user_id and role from token subject
    subject = payload.get("sub")
    if not subject or ":" not in subject:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )

    user_id, role = subject.split(":", 1)
    return user_id, role


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token_data: tuple[str, str] = Depends(get_current_user_token),
) -> User:
    """Get current client user."""
    user_id, role = token_data

    if role != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    return user


async def get_current_store(
    db: AsyncSession = Depends(get_db),
    token_data: tuple[str, str] = Depends(get_current_user_token),
) -> Store:
    """Get current store user."""
    user_id, role = token_data

    if role != "store":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    store = await db.get(Store, user_id)
    if store is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )

    if not store.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive store"
        )

    if not store.is_approved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Store not approved"
        )

    return store


async def get_current_admin(
    db: AsyncSession = Depends(get_db),
    token_data: tuple[str, str] = Depends(get_current_user_token),
) -> Admin:
    """Get current admin user."""
    user_id, role = token_data

    if role not in ["admin", "superadmin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    admin = await db.get(Admin, user_id)
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive admin"
        )

    return admin


async def get_current_active_user(
    db: AsyncSession = Depends(get_db),
    token_data: tuple[str, str] = Depends(get_current_user_token),
) -> Union[User, Store, Admin]:
    """Get current active user (client, store, or admin)."""
    user_id, role = token_data

    if role == "client":
        user = await db.get(User, user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=404, detail="User not found or inactive")
        return user
    elif role == "store":
        store = await db.get(Store, user_id)
        if not store or not store.is_active or not store.is_approved:
            raise HTTPException(status_code=404, detail="Store not found or inactive")
        return store
    elif role in ["admin", "superadmin"]:
        admin = await db.get(Admin, user_id)
        if not admin or not admin.is_active:
            raise HTTPException(status_code=404, detail="Admin not found or inactive")
        return admin
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid role"
        )