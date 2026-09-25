from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.enums import UserRole
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut, OrderUpdate
from app.services.order_service import order_service

router = APIRouter()


@router.post("/", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(
    *,
    db: AsyncSession = Depends(deps.get_db),
    order_in: OrderCreate,
    current_user: User = Depends(deps.get_current_user),
):
    return await order_service.create_order(
        db, order_in=order_in, owner_id=current_user.id
    )


@router.get("/", response_model=list[OrderOut])
async def get_orders(
    *,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    is_template: Optional[bool] = None,
):
    owner_id = (
        current_user.id if current_user.role == UserRole.CLIENT else None
    )
    return await order_service.get_orders(
        db, owner_id=owner_id, is_template=is_template
    )


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    order = await order_service.get_order_or_404(db, order_id)
    if (
        current_user.role == UserRole.CLIENT
        and order.owner_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail="Access denied")
    return order


@router.patch("/{order_id}", response_model=OrderOut)
async def update_order(
    order_id: int,
    order_in: OrderUpdate,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    return await order_service.update_order(
        db, order_id=order_id, order_in=order_in, current_user=current_user
    )


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    await order_service.delete_order(
        db, order_id=order_id, current_user=current_user
    )


@router.post("/{order_id}/confirm", response_model=OrderOut)
async def confirm_order_receipt(
    order_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):

    return await order_service.confirm_receipt(
        db, order_id=order_id, current_user=current_user
    )
