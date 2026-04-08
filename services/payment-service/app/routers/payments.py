from fastapi import APIRouter, Depends, Query, status
from uuid import UUID
from typing import List

from app.schemas.payments import PaymentRequest, PaymentResponse
from app.service.pay_service import PaymentService
from app.core.security import get_payment_service

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post(
    "/",
    response_model=dict,
    status_code=status.HTTP_201_CREATED
)
async def create_payment(
    payload: PaymentRequest,
    service: PaymentService = Depends(get_payment_service)
):
    """Create a new payment and verify the transaction"""
    return await service.create_payment(payload)


@router.get(
    "/user/{user_id}",
    response_model=dict
)
async def get_my_payments(
    user_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    service: PaymentService = Depends(get_payment_service)
):
    """Get a list of all the user's payments with pagination"""
    return await service.list_user_payments(
        user_id=user_id,
        page=page,
        page_size=page_size
    )