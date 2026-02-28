from rest_framework import serializers
from core.models.Worker import Worker
from core.serializers.CategorySerializer import CategorySerializer


class WorkerSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    user_name = serializers.SerializerMethodField()
    phone = serializers.CharField(source="user.phone", read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Worker
        fields = [
            "id",
            "user",
            "user_name",
            "category",
            "description",
            "experience_years",
            "latitude",
            "longitude",
            "is_verified",
            "created_at",
            "phone",
            "average_rating",
            "review_count",
        ]

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_average_rating(self, obj):
        if hasattr(obj, "average_rating_annotated"):
            v = obj.average_rating_annotated
            return round(v, 1) if v is not None else 0
        from django.db.models import Avg
        from core.models.Review import Review
        r = Review.objects.filter(worker=obj).aggregate(avg=Avg("rating"))
        return round(r["avg"], 1) if r["avg"] is not None else 0

    def get_review_count(self, obj):
        if hasattr(obj, "review_count_annotated"):
            return obj.review_count_annotated or 0
        from django.db.models import Count
        return obj.reviews.count() if hasattr(obj, "reviews") else 0
