from django.conf import settings
from django.db import models


class TelegramProfile(models.Model):
    """Профиль пользователя для отправки напоминаний в Telegram."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="telegram_profile",
    )
    chat_id = models.CharField(max_length=50, unique=True, verbose_name="Telegram Chat ID")

    class Meta:
        verbose_name = "Telegram-профиль"
        verbose_name_plural = "Telegram-профили"

    def __str__(self):
        return f"{self.user} ({self.chat_id})"
