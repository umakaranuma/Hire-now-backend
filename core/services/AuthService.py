"""
JWT and authentication helpers.
"""
from rest_framework_simplejwt.tokens import RefreshToken


class AuthService:
    """Service for token generation and auth-related logic."""

    @staticmethod
    def get_tokens_for_user(user):
        """Return access and refresh tokens for a user."""
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_id": user.id,
        }
