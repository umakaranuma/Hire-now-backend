"""
Firebase Admin SDK: verify ID tokens from Firebase Phone Auth (client-side OTP).
"""
import os
from dotenv import load_dotenv

load_dotenv()


class FirebaseAuthService:
    _initialized = False

    @staticmethod
    def init():
        """Initialize Firebase Admin SDK once."""
        if FirebaseAuthService._initialized:
            return

        path = os.getenv("FIREBASE_ADMIN_SDK_PATH")
        if not path or not os.path.exists(path):
            raise Exception(
                "Firebase Admin SDK JSON missing. Set FIREBASE_ADMIN_SDK_PATH in .env (e.g. firebase-adminsdk.json)."
            )

        import firebase_admin
        from firebase_admin import credentials

        cred = credentials.Certificate(path)
        firebase_admin.initialize_app(cred)
        FirebaseAuthService._initialized = True

    @staticmethod
    def verify_id_token(id_token: str) -> dict:
        """Verify Firebase ID token; return decoded claims (uid, phone_number, etc.)."""
        from firebase_admin import auth

        FirebaseAuthService.init()
        decoded = auth.verify_id_token(id_token)
        return decoded
