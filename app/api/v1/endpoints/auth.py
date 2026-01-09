from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_active_user
from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models import (
    User, UserCreate, UserLogin,
    Store, StoreCreate, StoreLogin,
    Admin, AdminLogin
)

router = APIRouter()


@router.post("/client/register", response_model=dict[str, Any])
async def register_client(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new client."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email.lower()))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = User(
        name=user_data.name,
        email=user_data.email.lower(),
        phone=user_data.phone,
        profile_image=user_data.profile_image,
        password=get_password_hash(user_data.password)
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=f"{user.id}:client",
        expires_delta=access_token_expires
    )

    return {
        "success": True,
        "message": "Usuario registrado exitosamente",
        "data": {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone
            },
            "token": access_token
        }
    }


@router.post("/client/login", response_model=dict[str, Any])
async def login_client(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login client user."""
    result = await db.execute(select(User).where(User.email == login_data.email.lower()))
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cuenta desactivada. Contacta al soporte."
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=f"{user.id}:client",
        expires_delta=access_token_expires
    )

    return {
        "success": True,
        "message": "Login exitoso",
        "data": {
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "profile_image": user.profile_image
            },
            "token": access_token
        }
    }


@router.post("/store/register", response_model=dict[str, Any])
async def register_store(
    store_data: StoreCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new store."""
    # Check if email already exists
    result = await db.execute(select(Store).where(Store.owner_email == store_data.owner_email.lower()))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create store (pending approval)
    store = Store(
        owner_name=store_data.owner_name,
        owner_email=store_data.owner_email.lower(),
        owner_phone=store_data.owner_phone,
        password=get_password_hash(store_data.password),
        store_name=store_data.store_name,
        description=store_data.description,
        address=store_data.address,
        latitude=store_data.latitude,
        longitude=store_data.longitude,
        delivery_fee=store_data.delivery_fee,
        delivery_time_min=store_data.delivery_time_min,
        delivery_time_max=store_data.delivery_time_max,
        open_time=store_data.open_time,
        close_time=store_data.close_time,
        is_approved=False
    )

    db.add(store)
    await db.commit()
    await db.refresh(store)

    return {
        "success": True,
        "message": "Tienda registrada. Pendiente de aprobación por el administrador.",
        "data": {
            "store": {
                "id": store.id,
                "store_name": store.store_name,
                "owner_email": store.owner_email,
                "is_approved": store.is_approved
            }
        }
    }


@router.post("/store/login", response_model=dict[str, Any])
async def login_store(
    login_data: StoreLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login store user."""
    result = await db.execute(select(Store).where(Store.owner_email == login_data.email.lower()))
    store = result.scalar_one_or_none()

    if not store or not verify_password(login_data.password, store.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    if not store.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tienda desactivada. Contacta al administrador."
        )

    if not store.is_approved:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tu tienda aún no ha sido aprobada. Por favor espera la aprobación del administrador."
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=f"{store.id}:store",
        expires_delta=access_token_expires
    )

    return {
        "success": True,
        "message": "Login exitoso",
        "data": {
            "store": {
                "id": store.id,
                "owner_name": store.owner_name,
                "owner_email": store.owner_email,
                "owner_phone": store.owner_phone,
                "store_name": store.store_name,
                "description": store.description,
                "image": store.image,
                "address": store.address,
                "delivery_fee": store.delivery_fee,
                "delivery_time_min": store.delivery_time_min,
                "delivery_time_max": store.delivery_time_max,
                "rating": store.rating,
                "is_open": store.is_open
            },
            "token": access_token
        }
    }


@router.post("/admin/login", response_model=dict[str, Any])
async def login_admin(
    login_data: AdminLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login admin user."""
    result = await db.execute(select(Admin).where(Admin.email == login_data.email.lower()))
    admin = result.scalar_one_or_none()

    if not admin or not verify_password(login_data.password, admin.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cuenta desactivada"
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=f"{admin.id}:admin",
        expires_delta=access_token_expires
    )

    return {
        "success": True,
        "message": "Login exitoso",
        "data": {
            "admin": {
                "id": admin.id,
                "name": admin.name,
                "email": admin.email,
                "phone": admin.phone,
                "role": admin.role
            },
            "token": access_token
        }
    }


@router.get("/profile", response_model=dict[str, Any])
async def get_profile(
    current_user = Depends(get_current_active_user)
):
    """Get current user profile."""
    return {
        "success": True,
        "data": current_user
    }