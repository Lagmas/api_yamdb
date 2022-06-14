from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from .validators import validate_year


class User(AbstractUser):
    USER_ROLE = 'user'
    MODERATOR_ROLE = 'moderator'
    ADMIN_ROLE = 'admin'
    ROLES = [
        (USER_ROLE, 'User'),
        (ADMIN_ROLE, 'Administrator'),
        (MODERATOR_ROLE, 'Moderator')
    ]
    bio = models.TextField('Биография', blank=True)
    confirmation_code = models.CharField(
        'Код подтверждения', blank=True, max_length=50
    )
    role = models.CharField(
        'Роль', max_length=50, choices=ROLES, default='user'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'], name='unique_user_email'
            )
        ]


class Category(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    slug = models.SlugField(
        verbose_name='Адрес',
        max_length=50,
        unique=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    slug = models.SlugField(
        verbose_name='Идентификатор',
        max_length=50,
        unique=True
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    year = models.IntegerField(
        verbose_name='Дата выхода',
        validators=[validate_year]
    )
    description = models.TextField(
        verbose_name='Описание',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        through='GenreTitle'
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True
    )
    rating = models.IntegerField(
        verbose_name='Рейтинг',
        null=True,
        default=None
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['name']


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        blank=True, null=True,
        on_delete=models.SET_NULL)
    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        blank=True, null=True,
        on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.title}, жанр - {self.genre}'

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'


class Review(models.Model):
    """Модель Review, в которой хранятся данные об отзыве.
    Содержит поля:
    - title - ссылка на произведение, к которому оставлен отзыв,
    - text - текст отзыва,
    - author - ссылка на автора отзыва,
    - score - из пользовательских оценок формируется усреднённая
              оценка произведения,
    - pub_date - дата и время публикации комментария
    """
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='reviews',
                              verbose_name='Произведение',
                              help_text='Произведение, на которое'
                                        'оставлен отзыв')
    text = models.TextField(verbose_name='Текст',
                            help_text='Введите текст отзыва')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='reviews',
                               verbose_name='Автор')
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[MinValueValidator(
                    1, message='Минимальная оценка 1'),
                    MaxValueValidator(
                    10, message='Максимальная оценка 10')])
    pub_date = models.DateTimeField(auto_now_add=True,
                                    db_index=True,
                                    verbose_name='Опубликован')

    class Meta:
        ordering = ['-pub_date']
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]

    def __str__(self):
        """Метод __str__ возвращает текст отзыва
        """
        return self.text


class Comment(models.Model):
    """Модель Comment, в которой хранятся данные о комментариях.
    Содержит поля:
    - review - ссылка на отзыв,
    - text - текст комментария,
    - author - ссылка на автора комментария,
    - pub_date - дата и время публикации комментария
    """
    review = models.ForeignKey(Review,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Отзыв')
    text = models.TextField(verbose_name='Текст',
                            help_text='Введите текст комментария')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    db_index=True,
                                    verbose_name='Опубликован')

    class Meta:
        ordering = ['-pub_date']
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        """Метод __str__ возвращает имя автора комментария
        """
        return self.author.username
