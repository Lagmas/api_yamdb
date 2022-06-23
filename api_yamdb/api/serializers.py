from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from reviews.models import Category, Comment, Genre, Review, Title, User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Сериализатор для включения данных, которые
    хотим отправить в ответ.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['confirmation_code'] = serializers.CharField(required=True)

        del self.fields['password']

    def validate(self, attrs):
        """Переопределяем валидатор под наши условия входных данных."""
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if user.confirmation_code != confirmation_code:
            raise ValidationError(detail='Код не корректный')
        data = {}
        return data


class CategorySerializer(serializers.ModelSerializer):
    """Категории, описание."""

    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class GenreSerializer(serializers.ModelSerializer):
    """Жанры, описание."""

    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class TitleSerializer(serializers.ModelSerializer):
    """Основной метод записи информации."""
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
        read_only_fields = ('id', 'title', 'pub_date')

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        author = self.context['request'].user
        title = self.context['view'].kwargs.get('title_id')
        if Review.objects.filter(author=author, title=title).exists():
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
