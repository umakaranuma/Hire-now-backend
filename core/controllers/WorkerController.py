from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from core.models.Worker import Worker
from core.serializers.WorkerSerializer import WorkerSerializer
from core.services.DistanceService import DistanceService
from mServices import ResponseService

DEFAULT_NEARBY_RADIUS_KM = 50


class WorkerController(APIView):
    """GET /api/workers/ - list workers (optional ?category=<id>)."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        qs = Worker.objects.select_related("user", "category").all()
        category_id = request.query_params.get("category")
        if category_id:
            qs = qs.filter(category_id=category_id)
        data = WorkerSerializer(qs, many=True).data
        return ResponseService.response("SUCCESS", result=data)


class WorkerDetailController(APIView):
    """GET /api/workers/<id>/ - worker detail."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        try:
            worker = Worker.objects.select_related("user", "category").get(pk=pk)
            return ResponseService.response("SUCCESS", result=WorkerSerializer(worker).data)
        except Worker.DoesNotExist:
            return ResponseService.response("NOT_FOUND", message="Worker not found")


class WorkerNearbyController(APIView):
    """GET /api/workers/nearby/?lat=&lng=&radius_km= - workers within radius (km)."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        lat = request.query_params.get("lat", type=float)
        lng = request.query_params.get("lng", type=float)
        radius_km = request.query_params.get("radius_km", type=float) or DEFAULT_NEARBY_RADIUS_KM
        if lat is None or lng is None:
            return ResponseService.response("VALIDATION_ERROR", message="lat and lng required")
        workers = list(
            Worker.objects.select_related("user", "category").filter(
                latitude__isnull=False, longitude__isnull=False
            )
        )
        nearby = [
            w
            for w in workers
            if DistanceService.calculate_distance(lat, lng, w.latitude, w.longitude)
            <= radius_km
        ]
        return ResponseService.response("SUCCESS", result=WorkerSerializer(nearby, many=True).data)
