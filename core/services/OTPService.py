"""
OTP generation and validation (use Redis in production).
"""
import random
import string
from datetime import datetime, timedelta
from django.utils import timezone

from core.models.OTP import OTP
from core.models.User import User


class OTPService:
    """Service for OTP generation and verification."""

    OTP_LENGTH = 6
    OTP_EXPIRY_MINUTES = 10

    @staticmethod
    def generate_otp(length=None):
        """Generate numeric OTP."""
        length = length or OTPService.OTP_LENGTH
        return "".join(random.choices(string.digits, k=length))

    @staticmethod
    def create_otp(phone, user=None):
        """Create and store OTP for phone. Returns the OTP code."""
        code = OTPService.generate_otp()
        expires_at = timezone.now() + timedelta(minutes=OTPService.OTP_EXPIRY_MINUTES)
        OTP.objects.create(phone=phone, code=code, expires_at=expires_at, user=user)
        return code

    @staticmethod
    def verify_otp(phone, code):
        """Verify OTP for phone. Returns True if valid."""
        otp = (
            OTP.objects.filter(phone=phone, code=code)
            .filter(expires_at__gt=timezone.now())
            .order_by("-created_at")
            .first()
        )
        return otp is not None
