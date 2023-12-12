from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Пермишшн автор или чтение."""
    def has_object_permission(self, request, view, obj):
        # Права на уровне объекта
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
