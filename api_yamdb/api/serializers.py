from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from reviews.models import Category, Comment, Genre, Review, Title, User


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username', 'email', 'role', 'bio', 'first_name', 'last_name'
        ]
        read_only_fields = ['role']


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'role', 'bio', 'first_name', 'last_name'
        ]

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )
        return email


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def __init__(self, *args, **kwargs):
        # наследуемся от класса-родителя
        super().__init__(*args, **kwargs)
        # Определяем новое поле
        self.fields['confirmation_code'] = serializers.CharField(required=True)

        # Удаляем поля по умолчанию от аутентификации django
        del self.fields['password']

    def validate(self, attrs):
        """Переопределяем валидатор под наши условия входных данных.
        """
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')

        # Если пользователя нет и код не корректный
        user = get_object_or_404(User, username=username)
        if user.confirmation_code != confirmation_code:
            raise ValidationError(detail='Код не корректный')

        # Отправка токена
        data = {}
        refresh = self.get_token(user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('email', 'username')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'

class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        source='reviews__score__avg', read_only=True
    )
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )

class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели Review.
    Список полей модели, которые будут сериализовать или
    десериализовать: 'title', 'text', 'author', 'score', 'pub_date'.
    Поля доступные только для чтения: 'id', 'author', 'pub_date'.
    Ключ author возвращает username автора.
    В сериализаторе имеется проверка:
    - уникальность пары: автор отзыва, произведение, на которое оставлен
    отзыв.
    """
    author = serializers.SlugRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
        slug_field='username')

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('id', 'author', 'title', 'pub_date')

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        user = self.context['request'].user
        title_id = self.context['view'].kwargs['title_id']
        if Review.objects.filter(author=user, title__id=title_id).exists():
            raise serializers.ValidationError(
                'Вы уже оставляли отзыв на это произведение!')
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели Comment.
    Список полей модели, которые будут сериализовать или
    десериализовать: 'id', 'review', 'text', 'author', 'pub_date'.
    Поля доступные только для чтения: 'id', 'review', 'pub_date'.
    Ключ author возвращает username автора.
    """
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('id', 'review', 'pub_date')
