from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg
from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from reviews.models import Category, Genre, Review, Title, Comment
from .mixins import ListCreateDestroyViewSet
from reviews.filters import TitlesFilter
from .permissions import (
    IsAuthorAdminModeratorOrReadOnly,
    IsAdminOrReadOnly
)
from .serializers import (
    CustomTokenObtainPairSerializer,
    CommentSerializer,
    ReviewSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    ReadOnlyTitleSerializer,
)


class CategoryViewSet(ListCreateDestroyViewSet):
    """
    Получить список всех категорий.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(ListCreateDestroyViewSet):
    """
    Получить список всех жанров.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """
    Получить список всех объектов.
    """
    queryset = Title.objects.all().annotate(
        Avg('reviews__score')
    ).order_by('name')
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return ReadOnlyTitleSerializer
        return TitleSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """Обработка выдачи токенов. Принимает набор учетных данных
    пользователя и возвращает пару веб-токенов для подтверждения
    аутентификации этих учетных данных.
    """
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет ReviewViewSet.
    Во вьюсете переопределяем метод perform_create().
    При создании отзыва значение автора берем из объекта request: в нем
    доступен экземпляр пользователя, которому принадлежит токен.
    Доступно всем:
    - получить список всех отзывов,
    - получить отзыв по id для указанного произведения.
    Доступно аутентифицированному пользователю:
    - добавить новый отзыв.
    Доступно автору отзыва, модератору или администратору:
    - частичное обновление отзыва по id,
    - удаление отзыва по id.
    """
    permission_classes = (IsAuthorAdminModeratorOrReadOnly,)
    serializer_class = ReviewSerializer

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return Review.objects.filter(title=self.get_title())

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет CommentViewSet.
    Во вьюсете переопределяем метод perform_create().
    - При создании комментария значение автора берем из объекта request: в нем
    доступен экземпляр пользователя, которому принадлежит токен.
    - Принадлежность комментария посту получаем через self.kwargs.
    Доступно всем:
    - получить список всех комментариев к отзыву,
    - получить комментарий для отзыва по id.
    Доступно аутентифицированному пользователю:
    - добавление комментария к отзыву.
    Доступно автору комментария, модератору или администратору:
    - частичное обновление комментария к отзыву по id,
    - удаление комментария по id.
    """
    permission_classes = (IsAuthorAdminModeratorOrReadOnly,)
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return Comment.objects.filter(review=self.get_review())

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
