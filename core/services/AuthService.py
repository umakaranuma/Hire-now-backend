"""
JWT and authentication helpers.
"""
from rest_framework_simplejwt.tokens import RefreshToken

from core.models.User import User


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

    @staticmethod
    def get_or_create_user_by_firebase(phone: str, firebase_uid: str):
        """
        Get or create a HireNow user from Firebase Phone Auth.
        Existing user: match by firebase_uid, optionally sync phone.
        New user: create with unusable password, phone + firebase_uid.
        """
        user = User.objects.filter(firebase_uid=firebase_uid).first()
        if user:
            if user.phone != phone:
                user.phone = phone
                user.save(update_fields=["phone"])
            return user

        # New user: unique username and email for AbstractUser
        username = f"fb_{firebase_uid[:30]}"
        email = f"{phone.replace('+', '').replace(' ', '')}@hirenow.firebase"
        user = User.objects.create_user(
            username=username,
            email=email,
            password=User.objects.make_random_password(length=32),
            phone=phone,
        )
        user.set_unusable_password()
        user.firebase_uid = firebase_uid
        user.save(update_fields=["firebase_uid"])
        return user

    @staticmethod
    def get_or_create_user_by_phone(phone: str):
        """
        Get or create a user by phone (dev mode OTP login).
        Used when verifying OTP via backend; no Firebase.
        """
        phone = (phone or "").strip()
        if not phone:
            return None
        user = User.objects.filter(phone=phone).first()
        if user:
            return user
        safe = phone.replace("+", "").replace(" ", "")[:30]
        username = f"phone_{safe}"
        if User.objects.filter(username=username).exists():
            username = f"phone_{safe}_{User.objects.count()}"
        email = f"{safe}@hirenow.dev"
        user = User.objects.create_user(
            username=username,
            email=email,
            password=User.objects.make_random_password(length=32),
            phone=phone,
        )
        user.set_unusable_password()
        user.save()
        return user
