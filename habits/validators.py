from rest_framework.exceptions import ValidationError


def validate_habit(data):
    """Валидация полей привычки по правилам «Атомных привычек»."""
    if data.get("reward") and data.get("related_habit"):
        raise ValidationError(
            "Нельзя указывать одновременно и награду, и связанную привычку."
        )

    duration = data.get("duration")
    if duration is not None and (duration <= 0 or duration > 120):
        raise ValidationError("Время выполнения должно быть от 1 до 120 секунд.")

    frequency = data.get("frequency")
    if frequency is not None and not 1 <= frequency <= 7:
        raise ValidationError(
            "Периодичность: не реже 1 раза в 7 дней (1–7 дней)."
        )

    related = data.get("related_habit")
    if related is not None and not getattr(related, "is_pleasant", False):
        raise ValidationError(
            "В связанные можно указывать только привычки с признаком приятной."
        )

    if data.get("is_pleasant"):
        if data.get("reward"):
            raise ValidationError(
                "У приятной привычки не может быть вознаграждения."
            )
        if data.get("related_habit") is not None:
            raise ValidationError(
                "У приятной привычки не может быть связанной привычки."
            )
