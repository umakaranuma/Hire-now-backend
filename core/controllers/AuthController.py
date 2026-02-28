import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate, get_user_model

from core.serializers.UserSerializer import UserSerializer
from core.services.AuthService import AuthService
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
