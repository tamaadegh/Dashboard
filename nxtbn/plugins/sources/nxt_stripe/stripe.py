import json
import stripe
from decimal import Decimal
from typing import Optional, Any, Dict
from nxtbn.order.models import Order
from nxtbn.payment.base import PaymentPlugin, PaymentResponse
from rest_framework import serializers, status
from rest_framework.response import Response
from nxtbn.payment.models import Payment
from nxtbn.settings import get_env_var
from datetime import datetime, timezone
from nxtbn.payment import PaymentMethod, PaymentStatus

STRIPE_SUCCESS_URL = get_env_var('STRIPE_SUCCESS_URL', 'http://localhost:3000/order/success')
STRIPE_CANCEL_URL = get_env_var('STRIPE_CANCEL_URL', 'http://localhost:3000/cart')
STRIPE_WEBHOOK_KEY = get_env_var('STRIPE_WEBHOOK_KEY', '')
STRIPE_SECRET_KEY =  get_env_var('STRIPE_SECRET_KEY', '')

stripe.api_key = STRIPE_SECRET_KEY

class StripeSerializer(serializers.Serializer):
    """"Need to define at least a serialize, dummy as it is cod, no additional payload will come from payment gateway"""
    pass

class StripeGateway(PaymentPlugin):
    """Stripe payment gateway implementation."""
    gateway_name = 'stripe'

    def authorize(self, amount: Decimal, order_id: str, **kwargs):
        """Authorize a payment with Stripe."""
        pass  # Implement authorization logic for Stripe

    def capture(self, amount: Decimal, order_id: str, **kwargs):
        """Capture a previously authorized payment with Stripe."""
        pass  # Implement capture logic for Stripe

    def cancel(self, order_id: str, **kwargs):
        """Cancel an authorized payment with Stripe."""
        pass  # Implement cancelation logic for Stripe

    def refund(self, payment_id: str, amount: str, **kwargs):
        """Refund a captured payment with Stripe."""
        payment = Payment.objects.get(pk=payment_id)
        payment_intent_id = payment.transaction_id

        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        charge_id = payment_intent["latest_charge"]

        amount = int(amount)

        try:
            refund = stripe.Refund.create(charge=charge_id, amount=amount)

            return PaymentResponse(
                success=True,
                transaction_id=refund.id,
                message="Refund successful",
                raw_data=refund,
                meta_data={"order_id": payment.order.pk}
            )
        except stripe.error.StripeError as e:
            return PaymentResponse(
                success=False,
                message=str(e),
                raw_data=e
            )

    def partial_refund(self, amount: Decimal, order_id: str, **kwargs):
       pass # Implement partial refund logic for Stripe

    def normalize_response(self, raw_response: Any) -> PaymentResponse:
        """Normalize the Stripe response to a consistent PaymentResponse."""
        pass  # Implement normalization logic for Stripe response

    def special_serializer(self):
        """Return a serializer for handling client-side payloads in API views."""
        return StripeSerializer()
        # Implement serializer for Stripe

    def public_keys(self) -> Dict[str, Any]:
        """
        Retrieve public keys and non-sensitive information required for secure communication and client-side operations with Stripe.
        """
        pass  # Implement method to retrieve public keys for Stripe

    def payment_url_with_meta(self, order, **kwargs) -> Dict[str, Any]:
        """
        Get payment URL and additional metadata based on the order ID for Stripe.
        """
        order_items = order.line_items.all()

        line_items = []
        for item in order_items:

            line_items.append({
            'price_data': {
                'currency': self.get_currency_code(),
                'unit_amount': self.to_subunit(item.price_per_unit),
                'product_data': {
                    'name': item.variant.name,
                    'description': '-----',
                    'images': ['https://example.com/t-shirt.png'],
            },
            },
            'quantity': item.quantity,
        })              
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=line_items,
                mode='payment',
                client_reference_id=order.alias,
                success_url=STRIPE_SUCCESS_URL,
                cancel_url=STRIPE_CANCEL_URL,
                metadata={"order_id": order.alias}
            )
        except Exception as e:
            return str(e)
        else:
            return {
                "url": checkout_session.url,
                "order_alias": order.alias,
            }

    def handle_webhook_event(self, request_data: Dict[str, Any], payment_plugin_id: str):
        """
        Handle a webhook event received from Stripe.
        """
        request = request_data
        endpoint_secret = STRIPE_WEBHOOK_KEY

        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        event = None
        
        if endpoint_secret:
            # Only verify the event if there is an endpoint secret defined
            # Otherwise use the basic event deserialized with json
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, endpoint_secret
                )
            except ValueError as e:
                # Invalid payload
                return Response(status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.SignatureVerificationError as e:
                # Invalid signature
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            # Handle the event
            if event.type == "checkout.session.completed":
                data = request.data
                order_alias = data["data"]["object"]["client_reference_id"]
                order = Order.objects.get(alias=order_alias)

                payment_payload = {
                    "order_alias": order_alias,
                    "payment_amount": data["data"]["object"]["amount_total"],
                    "gateway_response_raw": data,
                    "paid_at": datetime.fromtimestamp(int(data["data"]["object"]["created"]), tz=timezone.utc),
                    "transaction_id": data["data"]["object"]["payment_intent"],
                    "payment_method": PaymentMethod.CREDIT_CARD,
                    "payment_status": PaymentStatus.CAPTURED,
                    "order": order.pk,
                    "payment_plugin_id": payment_plugin_id,
                    "gateway_name": self.gateway_name,
                }

                self.create_payment_instance(payment_payload)

        return Response(status=status.HTTP_200_OK)