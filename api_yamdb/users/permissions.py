from rest_framework import permissions


class IsAdministratorRole(permissions.BasePermission):
    """Настройка прав доступа на уровне всего запроса."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
            or request.user.is_superuser
        )
