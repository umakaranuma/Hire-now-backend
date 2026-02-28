from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Avg, Count

from core.models.Worker import Worker
from core.serializers.WorkerSerializer import WorkerSerializer
from core.services.DistanceService import DistanceService
from mServices import ResponseService

DEFAULT_NEARBY_RADIUS_KM = 50


def worker_queryset():
    return Worker.objects.select_related("user", "category").annotate(
        average_rating_annotated=Avg("reviews__rating"),
        review_count_annotated=Count("reviews"),
    )


class WorkerController(APIView):
    """GET /api/workers/ - list workers (optional ?category=<id>, ?search=)."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        qs = worker_queryset()
        category = request.query_params.get("category", "").strip()
        if category:
            if category.isdigit():
                qs = qs.filter(category_id=int(category))
            else:
                qs = qs.filter(category__slug=category)
        search = request.query_params.get("search", "").strip()
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__username__icontains=search)
                | Q(category__name__icontains=search)
                | Q(category__slug__icontains=search)
            )
        data = WorkerSerializer(qs, many=True).data
        return ResponseService.response("SUCCESS", result=data)


class WorkerDetailController(APIView):
    """GET /api/workers/<id>/ - worker detail."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, worker_id):
        try:
            worker = worker_queryset().get(pk=worker_id)
            return ResponseService.response("SUCCESS", result=WorkerSerializer(worker).data)
        except Worker.DoesNotExist:
            return ResponseService.response("NOT_FOUND", message="Worker not found")


class WorkerNearbyController(APIView):
    """GET /api/workers/nearby/?lat=&lng=&radius_km= - workers within radius (km)."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        lat = request.query_params.get("lat", type=float)
        lng = request.query_params.get("lng", type=float)
        radius_km = request.query_params.get("radius_km", type=float) or request.query_params.get("radius", type=float) or DEFAULT_NEARBY_RADIUS_KM
        if lat is None or lng is None:
            return ResponseService.response("VALIDATION_ERROR", message="lat and lng required")
        qs = worker_queryset().filter(
            latitude__isnull=False, longitude__isnull=False
        )
        category_id = request.query_params.get("category")
        category_slug = request.query_params.get("category_slug")
        if category_id:
            qs = qs.filter(category_id=category_id)
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        workers = list(qs)
        nearby = [
            w
            for w in workers
            if DistanceService.calculate_distance(lat, lng, w.latitude, w.longitude)
            <= radius_km
        ]
        data = WorkerSerializer(nearby, many=True).data
        for i, w in enumerate(nearby):
            data[i]["distance"] = round(
                DistanceService.calculate_distance(lat, lng, w.latitude, w.longitude), 2
            )
        return ResponseService.response("SUCCESS", result=data)
