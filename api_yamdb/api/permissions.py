from rest_framework import permissions


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
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_admin
                or request.user.is_moderator
                )


class IsAdminOrReadOnly(permissions.BasePermission):
    """Позволяет предоставлять разные уровни доступа.
    Разным пользователям в зависимости от их свойств, позволяются
    различные действия над объектами.
    IsAdminOrReadOnly разрешает создавать, удалять, изменять
    объект только пользователю с ролью admin, остальным доступно
    только чтение.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    and request.user.is_admin)
                )
