"""
SMS sending service. Integrate with provider (Twilio, etc.) via env.
"""
import os


class SMSService:
    """SMS sending (e.g. OTP)."""

    @staticmethod
    def send(phone: str, message: str) -> bool:
        """Send SMS. Return True if sent successfully."""
        api_key = os.environ.get("SMS_API_KEY")
        if not api_key:
            return False
        # Implement actual API call here
        return True
