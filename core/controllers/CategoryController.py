from rest_framework.views import APIView

from core.models.Category import Category
from core.serializers.CategorySerializer import CategorySerializer
from mServices import ResponseService


class CategoryController(APIView):
    """GET /api/categories/ - list categories."""

    def get(self, request):
        categories = Category.objects.all()
        data = CategorySerializer(categories, many=True).data
        return ResponseService.response("SUCCESS", result=data)


class CategoryDetailController(APIView):
    """GET /api/categories/<id>/ - category detail."""

    def get(self, request, category_id):
        try:
            category = Category.objects.get(pk=category_id)
            return ResponseService.response("SUCCESS", result=CategorySerializer(category).data)
        except Category.DoesNotExist:
            return ResponseService.response("NOT_FOUND", message="Category not found")
