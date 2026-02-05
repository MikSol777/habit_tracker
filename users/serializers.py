from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя."""

    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        extra_kwargs = {"email": {"required": False}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
