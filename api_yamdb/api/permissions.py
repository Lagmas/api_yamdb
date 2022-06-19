from rest_framework import permissions


class IsAdministratorRole(permissions.BasePermission):
    # Настройка прав доступа на уровне всего запроса
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
            or request.user.is_superuser
        )


class IsAuthorAdminModeratorOrReadOnly(permissions.BasePermission):
    """Позволяет предоставлять разные уровни доступа.
    Разным пользователям в зависимости от их свойств, позволяются
    различные действия над объектами.
    IsAuthorAdminModeratorOrReadOnly разрешает:
    - moderator, admin - право удалять и редактировать любые отзывы и
    комментарии.
    - author - создателю объекта разрешено удаление и редактирование
    созданного объекта.
    """
    # Определяет права на уровне запроса и пользователя
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    # Определяет права на уровне объекта
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (obj.author == request.user
                or request.user.is_admin
                or request.user.is_moderator)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Позволяет предоставлять разные уровни доступа.
    Разным пользователям в зависимости от их свойств, позволяются
    различные действия над объектами.
    IsAdminOrReadOnly разрешает создавать, удалять, изменять
    объект только пользователю с ролью admin, остальным доступно
    только чтение.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin
