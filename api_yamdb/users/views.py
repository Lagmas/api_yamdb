import uuid

from django.conf import settings
from django.core.mail import send_mail
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from reviews.models import User
from .permissions import IsAdministratorRole
from .serializers import (
    CredentialsSerializer,
    UserRoleSerializer,
    UserSerializer,
)


class UsersViewSet(viewsets.ModelViewSet):
    """API для работы пользователями."""
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
        """Обработка эндпоинта users/me. Запрос и возможность
        редактирования информации профиля пользователя.
        """
        user = User.objects.get(username=request.user)
        serializer = UserRoleSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterUserViewSet(viewsets.ModelViewSet):
    """Обработка принимает на вход параметры POST запросом:
    email и username, генерирует verification_code,
    создает пользователя и отправляет
    код по указанной в параметре почте.
    """
    queryset = User.objects.all()
    serializer_class = CredentialsSerializer
    permission_classes = (AllowAny,)

    def create(self, request):
        data = {}
        serializer = CredentialsSerializer(data=request.data)
        if serializer.is_valid():
            confirmation_code = uuid.uuid4()
            data['confirmation_code'] = str(confirmation_code)
            serializer.save(confirmation_code=confirmation_code)
            mail_text = f'Код подтверждения {confirmation_code}'
            mail_theme = 'Код подтверждения'
            mail_from = settings.MAIL_FROM
            mail_to = serializer.data['email']
            send_mail(
                mail_theme, mail_text, mail_from, [mail_to],
                fail_silently=False
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
