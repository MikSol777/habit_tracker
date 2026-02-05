import os
import requests
from celery import shared_task
from django.utils import timezone


@shared_task
def send_telegram_reminder(chat_id, message):
    """Отправить одно напоминание в Telegram."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=10)


@shared_task
def send_habit_reminders():
    """
    Периодическая задача: отправить напоминания о привычках на текущее время.
    Вызывается Celery Beat каждую минуту.
    """
    from habits.models import Habit

    now = timezone.now().time()
    habits = Habit.objects.filter(
        time__hour=now.hour,
        time__minute=now.minute,
        user__telegram_profile__isnull=False,
    ).select_related("user", "user__telegram_profile")

    for habit in habits:
        chat_id = habit.user.telegram_profile.chat_id
        text = (
            f"Напоминание: {habit.action} в {habit.place} в {habit.time.strftime('%H:%M')}. "
            f"Время на выполнение: до {habit.duration} сек."
        )
        send_telegram_reminder.delay(chat_id, text)
