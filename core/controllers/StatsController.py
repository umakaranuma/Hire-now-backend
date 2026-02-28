from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db.models import Avg

from core.models.Worker import Worker
from core.models.User import User
from core.models.Category import Category
from mServices import ResponseService


class StatsController(APIView):
    """GET /api/stats/ - public stats for home page."""

    permission_classes = [AllowAny]

    def get(self, request):
        verified_count = Worker.objects.filter(is_verified=True).count()
        total_workers = Worker.objects.count()
        total_users = User.objects.count()
        categories_count = Category.objects.count()
        avg_rating = Worker.objects.aggregate(avg=Avg("reviews__rating"))["avg"]
        return ResponseService.response("SUCCESS", result={
            "verified_workers": verified_count,
            "total_workers": total_workers,
            "total_users": total_users,
            "categories_count": categories_count,
            "average_rating": round(float(avg_rating), 1) if avg_rating is not None else 0,
        })
