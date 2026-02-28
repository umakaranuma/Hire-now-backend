"""
Custom permission classes for API.
"""
from rest_framework import permissions


class IsWorker(permissions.BasePermission):
    """Allow only users with role 'worker'."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "worker"
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow write only for object owner."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, "user", None) == request.user or getattr(
            obj, "author", None
        ) == request.user
