import stripe
from typing import Optional

from app.core.config import get_settings

settings = get_settings()


class StripeGateway:
    def __init__(self, api_key: str):
        self.api_key = api_key
        stripe.api_key = api_key


    def create_checkout_session(self, amount: int, currency: str, payment_id: str, email: Optional[str]):
        client_reference_id = str(payment_id)

        return stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                'price_data':{
                    'currency': currency.lower(),
                    'unit_amount': amount,
                    'product_data': {
                        'name': 'Payment for event registration',
                    },
                },
                'quantity': 1,
            }],
            mode = 'payment',
            client_reference_id = client_reference_id,
            customer_email = email,
            success_url = settings.STRIPE_SUCCESS_URL,
            cancel_url = settings.STRIPE_CANCEL_URL,
        )

    def verify_webhook(self, payload: bytes, signature: str) -> stripe.Event:
        return stripe.Webhook.construct_event(
            payload, signature, settings.STRIPE_WEBHOOK_SECRET
        )

