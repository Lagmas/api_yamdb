from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from reviews.models import Category, Genre, Review, Title, User
from .permissions import (
    IsAuthorAdminModeratorOrReadOnly,
    IsAdministratorRole,
)
from .serializers import (
    CustomTokenObtainPairSerializer,
    CommentSerializer,
    RegisterSerializer,
    ReviewSerializer,
    UserRoleSerializer,
    UserSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    ReadOnlyTitleSerializer,
)

from django.db.models import Avg
from .mixins import ListCreateDestroyViewSet
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TitlesFilter

User = get_user_model()


# class CategoryViewSet(ListCreateDestroyViewSet):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = (IsAdministratorRole,)
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ("name",)
#     lookup_field = "slug"


# class GenreViewSet(ListCreateDestroyViewSet):
#     queryset = Genre.objects.all()
#     serializer_class = GenreSerializer
#     permission_classes = (IsAdministratorRole,)
#     filter_backends = (filters.SearchFilter,)
#     search_fields = ("name",)
#     lookup_field = "slug"


# class TitleViewSet(viewsets.ModelViewSet):
#     queryset = Title.objects.all().annotate(
#         Avg("reviews__score")
#     ).order_by("name")
#     serializer_class = TitleSerializer
#     permission_classes = (IsAdministratorRole,)
#     filter_backends = [DjangoFilterBackend]
#     filterset_class = TitlesFilter

#     def get_serializer_class(self):
#         if self.action in ("retrieve", "list"):
#             return ReadOnlyTitleSerializer
#         return TitleSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """Обработка выдачи токенов."""
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class UsersViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=username',)
    permission_classes = (IsAdministratorRole,)

    @action(
        detail=False, methods=['PATCH', 'GET'], url_path='me',
        permission_classes=[IsAuthenticated]
    )
    def me_user(self, request, pk=None):
        """Обработка эндпоинта users/me"""
        user = User.objects.get(username=request.user)
        serializer = UserRoleSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def send_confirmation_code(self, email, token):
        subject = 'Confirmation code'
        message = f'Confirmation code: {token}'
        from_email = settings.MAIL_FROM
        send_mail(subject, message, from_email, [email, ])

    def perform_create(self, serializer):
        email = serializer.validated_data.get('email')
        # создаем пользователя без пароля
        user, created = User.objects.get_or_create(email=email)
        # создаем confirmation_code, он же - пароль для пользователя
        confirmation_code = default_token_generator.make_token(user)
        # устанавливаем хэш-пароль для пользователя
        user.set_password(confirmation_code)
        # сохраняем пароль пользователя
        user.save()
        # отправляем confirmation_code на почту пользователя
        self.send_confirmation_code(email, confirmation_code)


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
