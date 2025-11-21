"""Eye Product endpoints"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.eye_product import (
    EyeProductCreate,
    EyeProductUpdate,
    EyeProductResponse,
)
from app.crud.eye_product import eye_product as crud_eye_product
from app.core.dependencies import get_current_admin_user
from app.core.exceptions import NotFoundException
from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

router = APIRouter(prefix="/eye-products", tags=["eye-products"])


@router.get("", response_model=list[EyeProductResponse])
async def list_eye_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    category: str = Query(None),
    brand: str = Query(None),
    available_only: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """
    List all eye products
    
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    - **category**: Filter by category (Sunglasses, Contact Lenses, Eye Drops, Frames, etc.)
    - **brand**: Filter by brand
    - **available_only**: Return only available products
    """
    if category:
        products, _ = await crud_eye_product.get_by_category(db, category, skip=skip, limit=limit)
    elif brand:
        products, _ = await crud_eye_product.get_by_brand(db, brand, skip=skip, limit=limit)
    elif available_only:
        products, _ = await crud_eye_product.get_available(db, skip=skip, limit=limit)
    else:
        products, _ = await crud_eye_product.get_active(db, skip=skip, limit=limit)
    
    return products


@router.get("/{product_id}", response_model=EyeProductResponse)
async def get_eye_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get eye product details"""
    product = await crud_eye_product.get(db, product_id)
    if not product:
        raise NotFoundException(detail="Eye product not found")
    
    return product


@router.post("", response_model=EyeProductResponse, status_code=201)
async def create_eye_product(
    product_in: EyeProductCreate,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Create new eye product (admin only)"""
    product = await crud_eye_product.create(db, product_in)
    return product


@router.put("/{product_id}", response_model=EyeProductResponse)
async def update_eye_product(
    product_id: int,
    product_in: EyeProductUpdate,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Update eye product (admin only)"""
    product = await crud_eye_product.get(db, product_id)
    if not product:
        raise NotFoundException(detail="Eye product not found")
    
    product = await crud_eye_product.update(db, product, product_in)
    return product


@router.delete("/{product_id}", status_code=204)
async def delete_eye_product(
    product_id: int,
    current_user = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete eye product (admin only)"""
    success = await crud_eye_product.delete(db, product_id)
    if not success:
        raise NotFoundException(detail="Eye product not found")
