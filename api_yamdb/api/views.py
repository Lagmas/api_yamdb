from django.shortcuts import get_object_or_404
from reviews.models import Comment, Category, Genre, Review, Title
from rest_framework import viewsets
from .permissions import IsAuthorAdminModeratorOrReadOnly
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    CustomTokenObtainPairSerializer,
    CommentSerializer,
    ReviewSerializer,
    GenreSerializer,
    CategorySerializer,
    TitleSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Обработка выдачи токенов."""
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


def get_review(self):
    return get_object_or_404(Review, pk=self.kwargs.get('review_id'))


def get_title(self):
    return get_object_or_404(Title, pk=self.kwargs.get('title_id'))


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
    permission_classes = [IsAuthorAdminModeratorOrReadOnly]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(title=get_title(self).id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        title=get_title(self))


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
    permission_classes = [IsAuthorAdminModeratorOrReadOnly]
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        print(get_review(self).id)
        return Comment.objects.filter(review=get_review(self).id)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user,
                        review=Review.objects.get(id=get_review(self).id))
