"""
PayHere payment gateway integration. Add credentials via env.
"""
import os


class PayHereService:
    """PayHere payment service (Sri Lanka)."""

    @staticmethod
    def get_merchant_id():
        return os.environ.get("PAYHERE_MERCHANT_ID", "")

    @staticmethod
    def create_payment_request(amount, order_id, return_url, cancel_url, **kwargs):
        """Build payment request payload for PayHere."""
        return {
            "merchant_id": PayHereService.get_merchant_id(),
            "amount": amount,
            "order_id": order_id,
            "return_url": return_url,
            "cancel_url": cancel_url,
            **kwargs,
        }
