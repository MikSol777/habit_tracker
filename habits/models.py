from django.conf import settings
from django.db import models


class Habit(models.Model):
    """Привычка: действие в время в месте. Полезная или приятная."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
    )
    place = models.CharField(max_length=255, verbose_name="Место")
    time = models.TimeField(verbose_name="Время")
    action = models.CharField(max_length=255, verbose_name="Действие")

    is_pleasant = models.BooleanField(default=False, verbose_name="Признак приятной привычки")
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_habits",
    )

    frequency = models.PositiveIntegerField(default=1, verbose_name="Периодичность (дней)")
    reward = models.CharField(max_length=255, null=True, blank=True, verbose_name="Вознаграждение")
    duration = models.PositiveIntegerField(verbose_name="Время на выполнение (сек)")
    is_public = models.BooleanField(default=False, verbose_name="Публичная")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.action
