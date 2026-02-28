from rest_framework import serializers
from core.models.Review import Review


class ReviewSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "worker",
            "author",
            "author_name",
            "rating",
            "comment",
            "created_at",
        ]
        read_only_fields = ["author"]

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.username
