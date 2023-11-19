from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminIsAuthorOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if (request.method in ['PUT', 'PATCH', 'DELETE']
                and not request.user.is_anonymous):
            return (
                request.user == obj.author
                or request.user.is_superuser
                or request.user.is_admin
            )
        return request.method in SAFE_METHODS
