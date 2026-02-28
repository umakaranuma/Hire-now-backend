from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from core.models.Review import Review
from core.models.Worker import Worker
from core.serializers.ReviewSerializer import ReviewSerializer
from mServices import ResponseService


class WorkerReviewsController(APIView):
    """GET /api/workers/<pk>/reviews/ - list reviews for worker. POST - create review (auth)."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, worker_id):
        try:
            Worker.objects.get(pk=worker_id)
        except Worker.DoesNotExist:
            return ResponseService.response("NOT_FOUND", message="Worker not found")
        qs = Review.objects.select_related("worker", "author").filter(worker_id=worker_id)
        data = ReviewSerializer(qs, many=True).data
        return ResponseService.response("SUCCESS", result=data)

    def post(self, request, worker_id):
        if not request.user.is_authenticated:
            return ResponseService.response("UNAUTHORIZED", message="Authentication required")
        try:
            worker = Worker.objects.get(pk=worker_id)
        except Worker.DoesNotExist:
            return ResponseService.response("NOT_FOUND", message="Worker not found")
        data = {**request.data, "worker": worker_id}
        serializer = ReviewSerializer(data=data)
        if not serializer.is_valid():
            return ResponseService.response(
                "VALIDATION_ERROR", message="Invalid data", result=serializer.errors
            )
        serializer.save(author=request.user)
        return ResponseService.response("SUCCESS", result=serializer.data)
