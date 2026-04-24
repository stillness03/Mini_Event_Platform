import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4
from fastapi import HTTPException
from app.models.payments import PaymentStatus
from app.schemas.payments import PaymentRequest


VALID_EVENT_ID = "69971f4fb59d31712c9b0b81"

@pytest.mark.asyncio
class TestCreatePayment:

    async def test_success(self, service, mock_deps):
        user_id = uuid4()
        req = PaymentRequest(
            user_id=user_id, event_id=VALID_EVENT_ID,
            amount=10, currency="USD", email="e@e.com",
            first_name="John", last_name="Doe",
        )

        mock_deps["event_client"].get_event.return_value = {"owner_id": str(uuid4())}
        mock_deps["repo"].get_by_event_and_user = AsyncMock(return_value=None)

        pay_mock = MagicMock(id=uuid4(), amount=100, currency="USD", email="test@test.com")
        mock_deps["repo"].create = AsyncMock(return_value=pay_mock)
        mock_deps["repo"].update_after_stripe = AsyncMock()
        mock_deps["repo"].commit = AsyncMock()

        session_mock = MagicMock(id="sess_123", url="https://stripe.com/pay")
        mock_deps["stripe_gateway"].create_checkout_session.return_value = session_mock

        result = await service.create_payment(req)

        assert result["payment_id"] == pay_mock.id
        assert result["checkout_url"] == "https://stripe.com/pay"
        mock_deps["repo"].update_after_stripe.assert_called_once()
        mock_deps["repo"].commit.assert_called()

    async def test_forbidden_own_event(self, service, mock_deps):
        user_id = uuid4()
        req = PaymentRequest(
            user_id=user_id, event_id=VALID_EVENT_ID,
            amount=10, currency="USD", email="e@e.com",
            first_name="John", last_name="Doe",
        )

        mock_deps["event_client"].get_event.return_value = {"owner_id": str(user_id)}

        with pytest.raises(HTTPException) as exc:
            await service.create_payment(req)
        assert exc.value.status_code == 403

    async def test_stripe_timeout_updates_status_to_failed(self, service, mock_deps):
        mock_deps["event_client"].get_event.return_value = {"owner_id": "other"}
        mock_deps["repo"].get_by_event_and_user = AsyncMock(return_value=None)

        pay_mock = MagicMock(id=uuid4(), amount=10, currency="USD")
        mock_deps["repo"].create = AsyncMock(return_value=pay_mock)
        mock_deps["repo"].update_status = AsyncMock()
        mock_deps["repo"].commit = AsyncMock()

        mock_deps["stripe_gateway"].create_checkout_session.side_effect = asyncio.TimeoutError()

        req = PaymentRequest(
            user_id=uuid4(), event_id=VALID_EVENT_ID,
            amount=10, currency="USD", email="e@e.com",
            first_name="John", last_name="Doe",
        )

        with pytest.raises(HTTPException) as exc:
            await service.create_payment(req)

        assert exc.value.status_code == 503
        mock_deps["repo"].update_status.assert_called_with(pay_mock.id, PaymentStatus.FAILED)

    async def test_event_service_timeout(self, service, mock_deps):
        mock_deps["event_client"].get_event.side_effect = asyncio.TimeoutError()

        req = PaymentRequest(
            user_id=uuid4(), event_id=VALID_EVENT_ID,
            amount=10, currency="USD", email="e@e.com",
            first_name="John", last_name="Doe",
        )

        with pytest.raises(HTTPException) as exc:
            await service.create_payment(req)

        assert exc.value.status_code == 503

    async def test_event_service_unavailable(self, service, mock_deps):
        from app.client.event_client import EventServiceUnavailable
        mock_deps["event_client"].get_event.side_effect = EventServiceUnavailable()

        req = PaymentRequest(
            user_id=uuid4(), event_id=VALID_EVENT_ID,
            amount=10, currency="USD", email="e@e.com",
            first_name="John", last_name="Doe",
        )

        with pytest.raises(HTTPException) as exc:
            await service.create_payment(req)

        assert exc.value.status_code == 503

    async def test_event_not_found(self, service, mock_deps):
        mock_deps["event_client"].get_event.return_value = None

        req = PaymentRequest(
            user_id=uuid4(), event_id=VALID_EVENT_ID,
            amount=10, currency="USD", email="e@e.com",
            first_name="John", last_name="Doe",
        )

        with pytest.raises(HTTPException) as exc:
            await service.create_payment(req)

        assert exc.value.status_code == 404

    async def test_already_paid(self, service, mock_deps):
        mock_deps["event_client"].get_event.return_value = {"owner_id": "other"}

        existing = MagicMock(id=uuid4(), status=PaymentStatus.SUCCESS)
        mock_deps["repo"].get_by_event_and_user = AsyncMock(return_value=existing)

        req = PaymentRequest(
            user_id=uuid4(), event_id=VALID_EVENT_ID,
            amount=10, currency="USD", email="e@e.com",
            first_name="John", last_name="Doe",
        )

        result = await service.create_payment(req)

        assert result["message"] == "Already paid"
        assert result["payment_id"] == existing.id

    async def test_payment_already_initiated(self, service, mock_deps):
        mock_deps["event_client"].get_event.return_value = {"owner_id": "other"}

        existing = MagicMock(
            id=uuid4(),
            status=PaymentStatus.REQUIRES_PAYMENT,
            checkout_url="https://stripe.com/existing",
        )
        mock_deps["repo"].get_by_event_and_user = AsyncMock(return_value=existing)

        req = PaymentRequest(
            user_id=uuid4(), event_id=VALID_EVENT_ID,
            amount=10, currency="USD", email="e@e.com",
            first_name="John", last_name="Doe",
        )

        result = await service.create_payment(req)

        assert result["message"] == "Payment already initiated"
        assert result["checkout_url"] == "https://stripe.com/existing"

@pytest.mark.asyncio
class TestConfirmPayment:

    async def test_confirm_success(self, service, mock_deps):
        stripe_id = "cs_test_123"
        payment_mock = MagicMock(id=uuid4(), status=PaymentStatus.REQUIRES_PAYMENT)
        mock_deps["repo"].get_by_stripe_id = AsyncMock(return_value=payment_mock)
        mock_deps["repo"].update_status = AsyncMock()
        mock_deps["repo"].commit = AsyncMock()

        await service.confirm_payment(stripe_id)

        mock_deps["repo"].update_status.assert_called_with(payment_mock.id, PaymentStatus.SUCCESS)
        mock_deps["repo"].commit.assert_called_once()

    async def test_confirm_already_confirmed(self, service, mock_deps):
        stripe_id = "cs_test_123"
        payment_mock = MagicMock(id=uuid4(), status=PaymentStatus.SUCCESS)
        mock_deps["repo"].get_by_stripe_id = AsyncMock(return_value=payment_mock)
        mock_deps["repo"].update_status = AsyncMock()

        await service.confirm_payment(stripe_id)

        mock_deps["repo"].update_status.assert_not_called()

    async def test_confirm_payment_not_found(self, service, mock_deps):
        mock_deps["repo"].get_by_stripe_id = AsyncMock(return_value=None)
        mock_deps["repo"].update_status = AsyncMock()

        await service.confirm_payment("nonexistent_id")

        mock_deps["repo"].update_status.assert_not_called()