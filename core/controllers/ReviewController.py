from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from core.models.Review import Review
from core.serializers.ReviewSerializer import ReviewSerializer
from mServices import ResponseService
from services.PermissionService import IsOwnerOrReadOnly


class ReviewController(APIView):
    """GET /api/reviews/ - list reviews. POST /api/reviews/ - create (auth). Optional ?worker_id=."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        qs = Review.objects.select_related("worker", "author").all()
        worker_id = request.query_params.get("worker_id")
        if worker_id:
            qs = qs.filter(worker_id=worker_id)
        data = ReviewSerializer(qs, many=True).data
        return ResponseService.response("SUCCESS", result=data)

    def post(self, request):
        if not request.user.is_authenticated:
            return ResponseService.response("UNAUTHORIZED", message="Authentication required")
        serializer = ReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return ResponseService.response(
                "VALIDATION_ERROR", message="Invalid data", result=serializer.errors
            )
        serializer.save(author=request.user)
        return ResponseService.response("SUCCESS", result=serializer.data)


class ReviewDetailController(APIView):
    """GET /api/reviews/<id>/ - detail. PUT/PATCH/DELETE - owner only."""

    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get(self, request, pk):
        try:
            review = Review.objects.select_related("worker", "author").get(pk=pk)
            return ResponseService.response("SUCCESS", result=ReviewSerializer(review).data)
        except Review.DoesNotExist:
            return ResponseService.response("NOT_FOUND", message="Review not found")

    def put(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
            if not IsOwnerOrReadOnly().has_object_permission(request, self, review):
                return ResponseService.response("FORBIDDEN", message="Not allowed")
            serializer = ReviewSerializer(review, data=request.data, partial=False)
            if not serializer.is_valid():
                return ResponseService.response(
                    "VALIDATION_ERROR", message="Invalid data", result=serializer.errors
                )
            serializer.save()
            return ResponseService.response("SUCCESS", result=serializer.data)
        except Review.DoesNotExist:
            return ResponseService.response("NOT_FOUND", message="Review not found")

    def delete(self, request, pk):
        try:
            review = Review.objects.get(pk=pk)
            if not IsOwnerOrReadOnly().has_object_permission(request, self, review):
                return ResponseService.response("FORBIDDEN", message="Not allowed")
            review.delete()
            return ResponseService.response("SUCCESS", result=None)
        except Review.DoesNotExist:
            return ResponseService.response("NOT_FOUND", message="Review not found")
