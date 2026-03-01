"""
Middleware for JWT authentication and role-based endpoint access.
"""
from mServices.ResponseService import ResponseService
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken
from django.urls import resolve, Resolver404

from core.models.User import User


class EndpointPermissionMiddleware:
    """
    Middleware to enforce authentication for API endpoints.
    Public endpoints (no token required): auth (login/register), categories, users, workers.
    Also catches invalid URLs and returns a proper 404 JSON response.
    """

    # Path prefixes that do not require authentication (no token)
    PUBLIC_PATH_PREFIXES = (
        "api/auth/login",
        "api/auth/register",
        "api/auth/send-otp",
        "api/auth/verify-otp",
        "api/auth/firebase/login",
        "api/auth/register-with-firebase",
        "api/auth/register-with-otp",
        "api/categories",
        "api/users",
        "api/workers",
    )

    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()

    def _is_public_path(self, path_info):
        """Return True if path is under a public prefix (no token required)."""
        # Normalize: strip slashes and collapse multiple slashes
        path = path_info.strip("/")
        path = "/".join(p for p in path.split("/") if p)
        if not path.startswith("api/"):
            return False
        for prefix in self.PUBLIC_PATH_PREFIXES:
            if path == prefix or path.startswith(prefix + "/"):
                return True
        # Explicitly allow auth endpoints by segment (in case of path quirks)
        if "auth/" in path and any(
            x in path for x in ("send-otp", "verify-otp", "register-with-otp", "register-with-firebase", "firebase/login", "auth/login", "auth/register")
        ):
            return True
        return False

    def __call__(self, request):
        try:
            setattr(request, "_dont_enforce_csrf_checks", True)

            # Only enforce JWT for /api/ paths
            if not request.path_info.startswith("/api/"):
                return self.get_response(request)

            try:
                resolved = resolve(request.path_info)
                resolved.route = getattr(resolved, "route", request.path_info)
            except Resolver404:
                return ResponseService.response(
                    "NOT_FOUND",
                    {
                        "endpoint": [
                            {
                                "error_type": "not_found",
                                "tokens": {"_attribute": "endpoint"},
                            }
                        ]
                    },
                    "Endpoint does not exist.",
                )

            if self._is_public_path(request.path_info):
                # Don't send Authorization to the view so DRF doesn't try to validate the token
                request.META.pop("HTTP_AUTHORIZATION", None)
                return self.get_response(request)

            auth_header = request.headers.get("Authorization", None)

            if not auth_header or not auth_header.startswith("Bearer "):
                return ResponseService.response(
                    "UNAUTHORIZED",
                    {
                        "token": [
                            {
                                "error_type": "required",
                                "tokens": {"_attribute": "token"},
                            }
                        ]
                    },
                    "Invalid authentication credentials.",
                )

            try:
                raw_token = auth_header.split(" ")[1]
                validated_token = self.jwt_auth.get_validated_token(raw_token)
                user_id = validated_token.get("user_id")

                if not user_id:
                    return ResponseService.response(
                        "UNAUTHORIZED",
                        {
                            "token": [
                                {
                                    "error_type": "invalid",
                                    "tokens": {"_attribute": "token"},
                                }
                            ]
                        },
                        "Invalid authentication credentials.",
                    )

                user = User.objects.filter(id=user_id).first()

                if not user:
                    return ResponseService.response(
                        "UNAUTHORIZED",
                        {
                            "user": [
                                {
                                    "error_type": "not_found",
                                    "tokens": {"_attribute": "user"},
                                }
                            ]
                        },
                        "Invalid authentication credentials.",
                    )

                request.user = user

            except InvalidToken:
                return ResponseService.response(
                    "UNAUTHORIZED",
                    {
                        "token": [
                            {
                                "error_type": "invalid",
                                "tokens": {"_attribute": "token"},
                            }
                        ]
                    },
                    "Token is invalid or expired.",
                )

            except AuthenticationFailed as e:
                return ResponseService.response(
                    "UNAUTHORIZED",
                    {
                        "token": [
                            {
                                "error_type": "authentication_failed",
                                "tokens": {"_attribute": "token"},
                            }
                        ]
                    },
                    str(e),
                )

        except Exception as e:
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR",
                {"error": str(e)},
                "An unexpected error occurred.",
            )

        return self.get_response(request)
