from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from core.models.User import User
from core.serializers.UserSerializer import UserSerializer
from mServices import ResponseService


class UserController(APIView):
    """GET /api/users/ - list users."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        users = User.objects.all()
        data = UserSerializer(users, many=True).data
        return ResponseService.response("SUCCESS", result=data)


class UserDetailController(APIView):
    """GET /api/users/<id>/ - user detail."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            return ResponseService.response("SUCCESS", result=UserSerializer(user).data)
        except User.DoesNotExist:
            return ResponseService.response("NOT_FOUND", message="User not found")
