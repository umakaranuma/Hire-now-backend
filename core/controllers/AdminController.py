from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from core.models.Worker import Worker
from core.models.User import User
from core.serializers.WorkerSerializer import WorkerSerializer
from mServices import ResponseService


class IsAdminUser(IsAuthenticated):
    """Allow only staff or role=admin."""

    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            and (getattr(request.user, "is_staff", False) or getattr(request.user, "role", None) == "admin")
        )


class AdminPendingWorkersController(APIView):
    """GET /api/admin/workers/pending/ - list workers with is_verified=False."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        from core.controllers.WorkerController import worker_queryset
        qs = worker_queryset().filter(is_verified=False)
        data = WorkerSerializer(qs, many=True).data
        list_data = []
        for w in data:
            list_data.append({
                **w,
                "name": w.get("user_name"),
                "category": w.get("category", {}) and w["category"].get("name") or "",
                "email": User.objects.filter(id=w.get("user")).values_list("email", flat=True).first() if w.get("user") else "",
            })
        return ResponseService.response("SUCCESS", result=list_data)


class AdminApproveWorkerController(APIView):
    """POST /api/admin/workers/<pk>/approve/ - set worker is_verified=True."""

    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            worker = Worker.objects.get(pk=pk)
            worker.is_verified = True
            worker.save()
            return ResponseService.response("SUCCESS", result=WorkerSerializer(worker).data)
        except Worker.DoesNotExist:
            return ResponseService.response("NOT_FOUND", message="Worker not found")


class AdminRejectWorkerController(APIView):
    """POST /api/admin/workers/<pk>/reject/ - optional reason."""

    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            worker = Worker.objects.get(pk=pk)
            worker.is_verified = False
            worker.save()
            return ResponseService.response("SUCCESS", result=None)
        except Worker.DoesNotExist:
            return ResponseService.response("NOT_FOUND", message="Worker not found")
