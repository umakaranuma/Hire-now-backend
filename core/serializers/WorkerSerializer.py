from rest_framework import serializers
from core.models.Worker import Worker
from core.serializers.CategorySerializer import CategorySerializer


class WorkerSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    user_name = serializers.SerializerMethodField()

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
        ]

    def get_user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
