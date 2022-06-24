from rest_framework import serializers

from reviews.models import User


class UserRoleSerializer(serializers.ModelSerializer):
    """Сериализатор ролей пользователей."""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'role', 'bio', 'first_name', 'last_name'
        )
        read_only_fields = ('role',)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователей."""
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'role', 'bio', 'first_name', 'last_name'
        )

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )
        return email

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует.'
            )
        return value


class CredentialsSerializer(serializers.ModelSerializer):
    """Сериализатор учетных данных."""
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email')
        extra_kwargs = {'password': {'required': False}}

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )
        return email

    def validate_username(self, value):
        username_me = value.lower()
        if 'me' == username_me:
            raise serializers.ValidationError(
                f'Создание Пользователя c username "{username_me}" запрещено'
            )
        return value


class RegisterSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователей."""
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ('email', 'username')
