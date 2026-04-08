from fastapi import Header, HTTPException, status, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.repositories.payments_rep import PaymentRepository
from app.service.pay_service import PaymentService

from app.client.event_client import EventClient, get_event_client
from shared import UserContext


def get_payment_repository(db: Session = Depends(get_db)):
    return PaymentRepository(db)

def get_payment_service(
    repo: PaymentRepository = Depends(get_payment_repository),
    event_client: EventClient = Depends(get_event_client)
):
    return PaymentService(repo, event_client)


def get_current_user(
        x_user_id: UUID = Header(None),
        x_user_role: str = Header("user")
    ) -> UserContext:
    if not x_user_id:
       raise HTTPException(
           status_code=status.HTTP_401_UNAUTHORIZED,
           detail="Unable to retrieve x_user_id",
       )

    return UserContext(
        user_id=x_user_id,
        role=x_user_role,
    )