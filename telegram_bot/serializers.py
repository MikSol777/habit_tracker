from rest_framework import serializers
from .models import TelegramProfile


class TelegramProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для привязки Telegram chat_id к пользователю."""

    class Meta:
        model = TelegramProfile
        fields = ("chat_id",)
        extra_kwargs = {"chat_id": {"required": True}}
