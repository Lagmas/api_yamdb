from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Данные о пользователе и список всех ролей.
    Добавление дополнительных полей.
    """
    USER_ROLE = 'user'
    MODERATOR_ROLE = 'moderator'
    ADMIN_ROLE = 'admin'
    ROLES = (
        (USER_ROLE, 'User'),
        (ADMIN_ROLE, 'Administrator'),
        (MODERATOR_ROLE, 'Moderator'),
    )
    bio = models.TextField('Биография', blank=True)
    confirmation_code = models.CharField(
        'Код подтверждения', blank=True, max_length=50
    )
    role = models.CharField(
        'Роль', max_length=50, choices=ROLES, default='user'
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN_ROLE

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR_ROLE

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'], name='unique_user_email'
            )
        ]
