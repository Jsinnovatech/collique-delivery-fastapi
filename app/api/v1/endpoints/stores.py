from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.api.deps import get_db, get_current_store, get_current_admin
from app.models import Store, StoreUpdate, StoreResponse, StorePublic

router = APIRouter()


@router.get("/", response_model=dict[str, Any])
async def get_stores(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    only_active: bool = True,
    only_approved: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Get list of stores."""
    query = select(Store)

    if only_active:
        query = query.where(Store.is_active == True)

    if only_approved:
        query = query.where(Store.is_approved == True)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            Store.store_name.ilike(search_pattern) |
            Store.address.ilike(search_pattern) |
            Store.description.ilike(search_pattern)
        )

    query = query.offset(skip).limit(limit).order_by(Store.rating.desc())

    result = await db.execute(query)
    stores = result.scalars().all()

    # Convert to public format
    stores_public = [
        StorePublic(
            id=store.id,
            store_name=store.store_name,
            description=store.description,
            image=store.image,
            address=store.address,
            latitude=store.latitude,
            longitude=store.longitude,
            delivery_fee=store.delivery_fee,
            delivery_time_min=store.delivery_time_min,
            delivery_time_max=store.delivery_time_max,
            open_time=store.open_time,
            close_time=store.close_time,
            rating=store.rating,
            total_reviews=store.total_reviews,
            is_open=store.is_open
        ) for store in stores
    ]

    return {
        "success": True,
        "data": stores_public,
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": len(stores_public)
        }
    }


@router.get("/{store_id}", response_model=dict[str, Any])
async def get_store(
    store_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get store by ID."""
    store = await db.get(Store, store_id)

    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )

    if not store.is_active or not store.is_approved:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not available"
        )

    store_public = StorePublic(
        id=store.id,
        store_name=store.store_name,
        description=store.description,
        image=store.image,
        address=store.address,
        latitude=store.latitude,
        longitude=store.longitude,
        delivery_fee=store.delivery_fee,
        delivery_time_min=store.delivery_time_min,
        delivery_time_max=store.delivery_time_max,
        open_time=store.open_time,
        close_time=store.close_time,
        rating=store.rating,
        total_reviews=store.total_reviews,
        is_open=store.is_open
    )

    return {
        "success": True,
        "data": store_public
    }


@router.put("/me", response_model=dict[str, Any])
async def update_my_store(
    store_update: StoreUpdate,
    current_store: Store = Depends(get_current_store),
    db: AsyncSession = Depends(get_db)
):
    """Update current store information."""
    update_data = store_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_store, field, value)

    await db.commit()
    await db.refresh(current_store)

    return {
        "success": True,
        "message": "Store updated successfully",
        "data": current_store
    }


@router.get("/me/profile", response_model=dict[str, Any])
async def get_my_store_profile(
    current_store: Store = Depends(get_current_store)
):
    """Get current store profile."""
    return {
        "success": True,
        "data": current_store
    }


# Admin endpoints
@router.get("/admin/pending", response_model=dict[str, Any])
async def get_pending_stores(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get pending approval stores (admin only)."""
    query = select(Store).where(
        and_(Store.is_approved == False, Store.is_active == True)
    ).offset(skip).limit(limit).order_by(Store.created_at.desc())

    result = await db.execute(query)
    stores = result.scalars().all()

    return {
        "success": True,
        "data": stores,
        "pagination": {
            "skip": skip,
            "limit": limit,
            "total": len(stores)
        }
    }


@router.post("/{store_id}/approve", response_model=dict[str, Any])
async def approve_store(
    store_id: str,
    current_admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Approve store (admin only)."""
    store = await db.get(Store, store_id)

    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )

    store.is_approved = True
    await db.commit()
    await db.refresh(store)

    return {
        "success": True,
        "message": "Store approved successfully",
        "data": store
    }


@router.post("/{store_id}/reject", response_model=dict[str, Any])
async def reject_store(
    store_id: str,
    current_admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """Reject/deactivate store (admin only)."""
    store = await db.get(Store, store_id)

    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )

    store.is_active = False
    store.is_approved = False
    await db.commit()
    await db.refresh(store)

    return {
        "success": True,
        "message": "Store rejected successfully",
        "data": store
    }