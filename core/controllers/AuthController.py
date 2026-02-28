from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model

from core.serializers.UserSerializer import UserSerializer, RegisterSerializer
from core.services.AuthService import AuthService
from mServices import ResponseService

User = get_user_model()


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ - returns JWT tokens and user."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200 and "access" in response.data:
            user = User.objects.get(username=request.data.get("username"))
            tokens = AuthService.get_tokens_for_user(user)
            return ResponseService.response(
                "SUCCESS", result={"tokens": tokens, "user": UserSerializer(user).data}
            )
        return response


class RegisterView(APIView):
    """POST /api/auth/register/ - create user and return JWT + user."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return ResponseService.response(
                "VALIDATION_ERROR", message="Invalid data", result=serializer.errors
            )
        user = serializer.save()
        tokens = AuthService.get_tokens_for_user(user)
        return ResponseService.response(
            "SUCCESS",
            result={"tokens": tokens, "user": UserSerializer(user).data},
        )
