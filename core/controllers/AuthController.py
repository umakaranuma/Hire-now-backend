import json
import os
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, get_user_model

from core.serializers.UserSerializer import UserSerializer
from core.services.AuthService import AuthService
from core.services.FirebaseAuthService import FirebaseAuthService
from core.services.OTPService import OTPService
from mServices import ResponseService, ValidatorService

User = get_user_model()


# --------------------------------------------------------
# POST /auth/login/ - Login and return JWT tokens + user
@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    """Handle POST (Login) for auth."""
    return do_login(request)


def do_login(request):
    """Authenticate user and return tokens + user."""
    try:
        data = json.loads(request.body) if request.body else {}

        rules = {
            "username": "required|max:150",
            "password": "required",
        }

        custom_messages = {
            "username.required": "Username is required.",
            "password.required": "Password is required.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        user = authenticate(
            request,
            username=data.get("username"),
            password=data.get("password"),
        )

        if user is None:
            return ResponseService.response(
                "UNAUTHORIZED",
                None,
                "Invalid username or password.",
            )

        tokens = AuthService.get_tokens_for_user(user)
        response_data = {
            "tokens": tokens,
            "user": UserSerializer(user).data,
        }

        return ResponseService.response(
            "SUCCESS",
            response_data,
            "Login successful.",
        )
    except json.JSONDecodeError as e:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {"body": ["Invalid JSON."]},
            "Invalid request body.",
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Server Error",
        )


# --------------------------------------------------------
# POST /auth/register/ - Register user and return JWT tokens + user
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    """Handle POST (Register) for auth."""
    return do_register(request)


def do_register(request):
    """Create user and return tokens + user."""
    try:
        data = json.loads(request.body) if request.body else {}

        rules = {
            "username": "required|max:150|unique:core_user,username",
            "email": "required|email",
            "password": "required|min:8",
            "phone": "max:20",
            "first_name": "max:150",
            "last_name": "max:150",
            "role": "in:customer,worker,admin",
        }

        custom_messages = {
            "username.required": "Username is required.",
            "username.unique": "This username already exists.",
            "email.required": "Email is required.",
            "email.email": "Enter a valid email address.",
            "password.required": "Password is required.",
            "password.min_string": "Password must be at least 8 characters.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        user = User.objects.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            phone=data.get("phone", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            role=data.get("role", "customer"),
        )

        tokens = AuthService.get_tokens_for_user(user)
        response_data = {
            "tokens": tokens,
            "user": UserSerializer(user).data,
        }

        return ResponseService.response(
            "SUCCESS",
            response_data,
            "Registration successful.",
        )
    except json.JSONDecodeError as e:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {"body": ["Invalid JSON."]},
            "Invalid request body.",
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Server Error",
        )


# --------------------------------------------------------
# POST /auth/send-otp - Send OTP to phone
@api_view(["POST"])
@permission_classes([AllowAny])
def send_otp(request):
    """Handle POST (Send OTP) for auth."""
    return do_send_otp(request)


def do_send_otp(request):
    """
    Create OTP for phone and optionally send via SMS (legacy).
    When using Firebase flow (Login / Register), OTP is sent by Firebase from the client
    via signInWithPhoneNumber — not this endpoint. This endpoint is for optional SMS fallback.
    """
    try:
        data = json.loads(request.body) if request.body else {}

        rules = {
            "phone": "required|max:20",
        }

        custom_messages = {
            "phone.required": "Phone number is required.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        phone = data["phone"].strip()
        code = OTPService.create_otp(phone)

        # Try to send SMS if configured (SMS_API_KEY + provider in integrations/SMSService)
        sms_sent = False
        try:
            from integrations.SMSService import SMSService
            sms_sent = SMSService.send(phone, f"Your verification code is: {code}")
        except Exception:
            pass

        result = {"message": "OTP sent successfully.", "success": True}
        # Development mode only: return OTP in response — show in console, user enters manually (Option 1)
        dev_otp = getattr(settings, "DEBUG", False) or os.environ.get("DEBUG_OTP_IN_RESPONSE", "").lower() in ("1", "true", "yes")
        if dev_otp and not sms_sent:
            result["otp_debug"] = code
            result["otp"] = code  # backwards compatibility
            result["note"] = "Dev mode: OTP returned for testing. Do not use in production."
        elif not sms_sent:
            result["note"] = "SMS not sent. Set DEBUG_OTP_IN_RESPONSE=1 in .env for dev mode (OTP in response)."

        return ResponseService.response(
            "SUCCESS",
            result,
            "OTP sent successfully.",
        )
    except json.JSONDecodeError:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {"body": ["Invalid JSON."]},
            "Invalid request body.",
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Server Error",
        )


# --------------------------------------------------------
# POST /auth/verify-otp - Verify OTP and login (dev mode: use after send-otp returns otp_debug)
@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):
    """Verify OTP for phone and return JWT + user (get or create user by phone)."""
    return do_verify_otp(request)


def do_verify_otp(request):
    try:
        data = json.loads(request.body) if request.body else {}
        rules = {"phone": "required|max:20", "otp": "required|max:10"}
        custom_messages = {"phone.required": "Phone number is required.", "otp.required": "OTP is required."}
        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        phone = (data.get("phone") or "").strip()
        code = (data.get("otp") or "").strip()
        if not OTPService.verify_otp(phone, code):
            return ResponseService.response(
                "UNAUTHORIZED",
                {"otp": ["Invalid or expired OTP."]},
                "Invalid or expired OTP.",
            )

        user = AuthService.get_or_create_user_by_phone(phone)
        if not user:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"phone": ["Invalid phone."]},
                "Invalid phone.",
            )
        tokens = AuthService.get_tokens_for_user(user)
        response_data = {"tokens": tokens, "user": UserSerializer(user).data}
        return ResponseService.response("SUCCESS", response_data, "Login successful.")
    except json.JSONDecodeError:
        return ResponseService.response("VALIDATION_ERROR", {"body": ["Invalid JSON."]}, "Invalid request body.")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


# --------------------------------------------------------
# POST /auth/firebase/login - Exchange Firebase ID token for HireNow JWT
@api_view(["POST"])
@permission_classes([AllowAny])
def firebase_login(request):
    """Handle POST (Firebase login): verify Firebase ID token, return JWT + user."""
    return do_firebase_login(request)


# --------------------------------------------------------
# POST /auth/register-with-firebase - Register with Firebase Phone Auth (OTP sent via Firebase)
@api_view(["POST"])
@permission_classes([AllowAny])
def register_with_firebase(request):
    """Register after Firebase Phone Auth: verify ID token, create user (and worker if role=worker)."""
    return do_register_with_firebase(request)


# --------------------------------------------------------
# POST /auth/register-with-otp - Register with backend OTP (dev mode: use after send-otp returns otp_debug)
@api_view(["POST"])
@permission_classes([AllowAny])
def register_with_otp(request):
    """Verify OTP then create user (and worker if role=worker). Dev mode only."""
    return do_register_with_otp(request)


def do_register_with_otp(request):
    """Verify OTP for phone, then create user and optionally worker profile."""
    try:
        data = json.loads(request.body) if request.body else {}
        rules = {
            "phone": "required|max:20",
            "otp": "required|max:10",
            "first_name": "required|max:150",
            "last_name": "max:150",
            "email": "nullable|email",
            "role": "in:customer,worker",
        }
        custom_messages = {
            "phone.required": "Phone number is required.",
            "otp.required": "OTP is required.",
            "first_name.required": "First name is required.",
        }
        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        phone = (data.get("phone") or "").strip()
        code = (data.get("otp") or "").strip()
        if not OTPService.verify_otp(phone, code):
            return ResponseService.response(
                "UNAUTHORIZED",
                {"otp": ["Invalid or expired OTP."]},
                "Invalid or expired OTP.",
            )

        first_name = (data.get("first_name") or "").strip()
        last_name = (data.get("last_name") or "").strip()
        email = (data.get("email") or "").strip()
        role = data.get("role", "customer")

        existing_user = User.objects.filter(phone=phone).first()
        if existing_user:
            # Phone already registered: allow upgrading to worker (add/update worker profile)
            if role == "worker":
                existing_user.first_name = first_name or existing_user.first_name
                existing_user.last_name = last_name or existing_user.last_name
                if email:
                    existing_user.email = email
                existing_user.role = "worker"
                existing_user.save(update_fields=["first_name", "last_name", "email", "role"])
                from core.models.Worker import Worker
                from core.models.Category import Category
                category_id = data.get("category")
                category = None
                if category_id:
                    try:
                        category = Category.objects.get(pk=category_id)
                    except (Category.DoesNotExist, ValueError, TypeError):
                        return ResponseService.response(
                            "VALIDATION_ERROR",
                            {"category": ["Invalid category."]},
                            "Validation Error",
                        )
                description = (data.get("description") or "").strip() or "No description"
                experience_years = int(data.get("experience_years", 0) or 0)
                try:
                    lat = float(data.get("latitude")) if data.get("latitude") is not None else 0.0
                    lng = float(data.get("longitude")) if data.get("longitude") is not None else 0.0
                except (TypeError, ValueError):
                    lat, lng = 0.0, 0.0
                worker, created = Worker.objects.get_or_create(
                    user=existing_user,
                    defaults={
                        "category": category,
                        "description": description,
                        "experience_years": max(0, experience_years),
                        "latitude": lat,
                        "longitude": lng,
                    },
                )
                if not created:
                    worker.category = category
                    worker.description = description
                    worker.experience_years = max(0, experience_years)
                    worker.latitude = lat
                    worker.longitude = lng
                    worker.save()
                user = existing_user
            else:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"phone": ["This phone is already registered. Please log in."]},
                    "Already registered.",
                )
        else:
            # New user: create account and optional worker profile
            username = (data.get("username") or "").strip()
            if not username and email:
                username = email.split("@")[0].replace(".", "_")[:150]
            if not username:
                username = f"otp_{phone.replace('+', '').replace(' ', '')[:20]}"
            if User.objects.filter(username=username).exists():
                username = f"{username}_{phone[-6:].replace(' ', '')}"

            email_for_user = email or f"{phone.replace('+', '').replace(' ', '')}@hirenow.dev"
            password = (data.get("password") or "").strip()
            if not password:
                password = User.objects.make_random_password(length=32)

            user = User.objects.create_user(
                username=username,
                email=email_for_user,
                password=password,
                phone=phone,
                first_name=first_name,
                last_name=last_name,
                role=role,
            )
            user.set_unusable_password()
            user.save(update_fields=[])

            if role == "worker":
                from core.models.Worker import Worker
                from core.models.Category import Category
                category_id = data.get("category")
                category = None
                if category_id:
                    try:
                        category = Category.objects.get(pk=category_id)
                    except (Category.DoesNotExist, ValueError, TypeError):
                        return ResponseService.response(
                            "VALIDATION_ERROR",
                            {"category": ["Invalid category."]},
                            "Validation Error",
                        )
                description = (data.get("description") or "").strip() or "No description"
                experience_years = int(data.get("experience_years", 0) or 0)
                lat = data.get("latitude")
                lng = data.get("longitude")
                try:
                    lat = float(lat) if lat is not None else 0.0
                    lng = float(lng) if lng is not None else 0.0
                except (TypeError, ValueError):
                    lat, lng = 0.0, 0.0
                Worker.objects.create(
                    user=user,
                    category=category,
                    description=description,
                    experience_years=max(0, experience_years),
                    latitude=lat,
                    longitude=lng,
                )

        tokens = AuthService.get_tokens_for_user(user)
        response_data = {"tokens": tokens, "user": UserSerializer(user).data}
        return ResponseService.response("SUCCESS", response_data, "Registration successful.")
    except json.JSONDecodeError:
        return ResponseService.response(
            "VALIDATION_ERROR", {"body": ["Invalid JSON."]}, "Invalid request body."
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


def do_register_with_firebase(request):
    """Verify Firebase ID token, then create user and optionally worker profile."""
    try:
        data = json.loads(request.body) if request.body else {}
        rules = {
            "firebase_id_token": "required",
            "first_name": "required|max:150",
            "last_name": "max:150",
            "email": "nullable|email",
            "role": "in:customer,worker",
        }
        custom_messages = {
            "firebase_id_token.required": "Firebase ID token is required.",
            "first_name.required": "First name is required.",
        }
        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        id_token = (data.get("firebase_id_token") or "").strip()
        if not id_token:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"firebase_id_token": [{"error_type": "required", "tokens": {"_attribute": "firebase_id_token"}}]},
                "Firebase ID token is required.",
            )

        try:
            decoded = FirebaseAuthService.verify_id_token(id_token)
        except Exception:
            return ResponseService.response(
                "UNAUTHORIZED",
                {"token": [{"error_type": "invalid", "tokens": {"_attribute": "token"}}]},
                "Firebase token is invalid or expired.",
            )

        phone = decoded.get("phone_number")
        firebase_uid = decoded.get("uid")
        if not phone or not firebase_uid:
            return ResponseService.response(
                "UNAUTHORIZED",
                {"token": [{"error_type": "invalid", "tokens": {"_attribute": "token"}}]},
                "Invalid Firebase token payload.",
            )

        # Already registered with this Firebase UID → reject (they should use Login)
        if User.objects.filter(firebase_uid=firebase_uid).exists():
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"firebase": ["This phone is already registered. Please log in."]},
                "Already registered.",
            )

        first_name = (data.get("first_name") or "").strip()
        last_name = (data.get("last_name") or "").strip()
        email = (data.get("email") or "").strip()
        role = data.get("role", "customer")

        username = (data.get("username") or "").strip()
        if not username and email:
            username = email.split("@")[0].replace(".", "_")[:150]
        if not username:
            username = f"fb_{firebase_uid[:30]}"
        if User.objects.filter(username=username).exists():
            username = f"{username}_{firebase_uid[:8]}"

        email_for_user = email or f"{phone.replace('+', '').replace(' ', '')}@hirenow.firebase"
        password = (data.get("password") or "").strip()
        if not password:
            password = User.objects.make_random_password(length=32)

        user = User.objects.create_user(
            username=username,
            email=email_for_user,
            password=password,
            phone=phone,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        user.set_unusable_password()
        user.firebase_uid = firebase_uid
        user.save(update_fields=["firebase_uid"])

        if role == "worker":
            from core.models.Worker import Worker
            from core.models.Category import Category
            category_id = data.get("category")
            if not category_id:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"category": ["Category is required for workers."]},
                    "Validation Error",
                )
            try:
                category = Category.objects.get(pk=category_id)
            except (Category.DoesNotExist, ValueError, TypeError):
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"category": ["Invalid category."]},
                    "Validation Error",
                )
            description = (data.get("description") or "").strip() or "No description"
            experience_years = int(data.get("experience_years", 0) or 0)
            lat = data.get("latitude")
            lng = data.get("longitude")
            try:
                lat = float(lat) if lat is not None else 0.0
                lng = float(lng) if lng is not None else 0.0
            except (TypeError, ValueError):
                lat, lng = 0.0, 0.0
            Worker.objects.create(
                user=user,
                category=category,
                description=description,
                experience_years=max(0, experience_years),
                latitude=lat,
                longitude=lng,
            )

        tokens = AuthService.get_tokens_for_user(user)
        response_data = {
            "tokens": tokens,
            "user": UserSerializer(user).data,
        }
        return ResponseService.response(
            "SUCCESS",
            response_data,
            "Registration successful.",
        )
    except json.JSONDecodeError:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {"body": ["Invalid JSON."]},
            "Invalid request body.",
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Server Error",
        )


def do_firebase_login(request):
    """Verify Firebase ID token, get or create user, return JWT and user."""
    try:
        data = json.loads(request.body) if request.body else {}

        rules = {
            "firebase_id_token": "required",
        }
        custom_messages = {
            "firebase_id_token.required": "Firebase ID token is required.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        id_token = (data.get("firebase_id_token") or "").strip()
        if not id_token:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"firebase_id_token": [{"error_type": "required", "tokens": {"_attribute": "firebase_id_token"}}]},
                "Firebase ID token is required.",
            )

        try:
            decoded = FirebaseAuthService.verify_id_token(id_token)
        except Exception as e:
            return ResponseService.response(
                "UNAUTHORIZED",
                {"token": [{"error_type": "invalid", "tokens": {"_attribute": "token"}}]},
                "Firebase token is invalid or expired.",
            )

        phone = decoded.get("phone_number")
        firebase_uid = decoded.get("uid")
        if not phone or not firebase_uid:
            return ResponseService.response(
                "UNAUTHORIZED",
                {"token": [{"error_type": "invalid", "tokens": {"_attribute": "token"}}]},
                "Invalid Firebase token payload.",
            )

        user = AuthService.get_or_create_user_by_firebase(phone=phone, firebase_uid=firebase_uid)
        tokens = AuthService.get_tokens_for_user(user)
        response_data = {
            "tokens": tokens,
            "user": UserSerializer(user).data,
        }

        return ResponseService.response(
            "SUCCESS",
            response_data,
            "Login successful.",
        )
    except json.JSONDecodeError:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {"body": ["Invalid JSON."]},
            "Invalid request body.",
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Server Error",
        )
