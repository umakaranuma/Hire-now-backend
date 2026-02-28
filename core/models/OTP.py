from django.db import models
from core.models.User import User


class OTP(models.Model):
    """OTP storage (replace with Redis in production)."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=20)
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = "core_otp"
        ordering = ["-created_at"]
