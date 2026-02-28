from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Avg, Count

from core.models.Worker import Worker
from core.serializers.WorkerSerializer import WorkerSerializer
from core.services.DistanceService import DistanceService
from mServices import ResponseService, ValidatorService, QueryBuilderService

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
    """GET /api/workers/nearby?lat=&lng=&radius_km= - workers within radius (km)."""

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        return get_workers_nearby(request)


def get_workers_nearby(request):
    """Get workers within radius using ValidatorService, QueryBuilderService, ResponseService."""
    try:
        # Build data from query params for validation
        data = {
            "lat": request.GET.get("lat", "").strip() or None,
            "lng": request.GET.get("lng", "").strip() or None,
            "radius_km": request.GET.get("radius_km", "").strip() or request.GET.get("radius", "").strip() or None,
            "category": request.GET.get("category", "").strip() or None,
            "category_slug": request.GET.get("category_slug", "").strip() or None,
        }

        rules = {
            "lat": "required|numeric",
            "lng": "required|numeric",
            "radius_km": "nullable|numeric",
            "category": "nullable|numeric",
            "category_slug": "nullable|max:255",
        }

        custom_messages = {
            "lat.required": "Latitude is required.",
            "lat.numeric": "Latitude must be a number.",
            "lng.required": "Longitude is required.",
            "lng.numeric": "Longitude must be a number.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        lat = float(data["lat"])
        lng = float(data["lng"])
        radius_km = float(data["radius_km"]) if data.get("radius_km") else DEFAULT_NEARBY_RADIUS_KM
        category_id = int(data["category"]) if data.get("category") and data["category"].isdigit() else None
        category_slug = data.get("category_slug") or None

        # QueryBuilderService: workers with lat/lng, optional category filter
        if category_slug:
            query = (
                QueryBuilderService("core_worker")
                .select("core_worker.id", "core_worker.latitude", "core_worker.longitude")
                .whereNotNull("core_worker.latitude")
                .whereNotNull("core_worker.longitude")
                .leftJoin("core_category", "core_worker.category_id", "core_category.id")
                .where("core_category.slug", category_slug)
            )
        else:
            query = (
                QueryBuilderService("core_worker")
                .select("id", "latitude", "longitude")
                .whereNotNull("latitude")
                .whereNotNull("longitude")
            )
            if category_id:
                query = query.where("category_id", category_id)
        rows = query.get()

        # Filter by distance and sort by distance
        ids_with_distance = []
        for row in rows:
            row_id = row.get("id") or row.get("core_worker.id")
            lat_key = "latitude" if "latitude" in row else "core_worker.latitude"
            lng_key = "longitude" if "longitude" in row else "core_worker.longitude"
            row_lat = row.get(lat_key)
            row_lng = row.get(lng_key)
            if row_lat is None or row_lng is None:
                continue
            try:
                row_lat = float(row_lat)
                row_lng = float(row_lng)
            except (TypeError, ValueError):
                continue
            dist = DistanceService.calculate_distance(lat, lng, row_lat, row_lng)
            if dist <= radius_km:
                ids_with_distance.append((row_id, round(dist, 2)))
        ids_with_distance.sort(key=lambda x: x[1])
        ids_ordered = [x[0] for x in ids_with_distance]
        distance_by_id = {x[0]: x[1] for x in ids_with_distance}

        if not ids_ordered:
            return ResponseService.response(
                "SUCCESS",
                [],
                "No workers found within the given radius.",
            )

        workers = worker_queryset().filter(pk__in=ids_ordered)
        workers_by_id = {w.id: w for w in workers}
        ordered_workers = [workers_by_id[i] for i in ids_ordered if i in workers_by_id]
        result = WorkerSerializer(ordered_workers, many=True).data
        for i, w in enumerate(ordered_workers):
            result[i]["distance"] = distance_by_id.get(w.id)

        return ResponseService.response(
            "SUCCESS",
            result,
            "Workers retrieved successfully.",
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "An unexpected error occurred.",
        )
