from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "firebase_uid",
            "role",
            "first_name",
            "last_name",
        ]
        read_only_fields = ["id", "role", "firebase_uid"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "phone",
            "first_name",
            "last_name",
            "role",
        ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
