from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Пермишшн автор или чтение."""
    def has_permission(self, request, view):
        # Права на уровне запроса и пользователя
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        # Права на уровне объекта
        return obj.author == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """Пермишшн админ или чтение."""
    def has_permission(self, request, view):
        # Права на уровне запроса и пользователя
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_staff)
