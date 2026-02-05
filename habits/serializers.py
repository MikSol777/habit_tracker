from rest_framework import serializers
from .models import Habit
from .validators import validate_habit


class HabitSerializer(serializers.ModelSerializer):
    """Сериализатор привычки. Поле user только для чтения."""

    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Habit
        fields = (
            "id",
            "user",
            "place",
            "time",
            "action",
            "is_pleasant",
            "related_habit",
            "frequency",
            "reward",
            "duration",
            "is_public",
            "created_at",
        )

    def validate(self, data):
        validate_habit(data)
        request = self.context.get("request")
        if request and data.get("related_habit"):
            if data["related_habit"].user_id != request.user.id:
                raise serializers.ValidationError(
                    "Связанной привычкой может быть только своя приятная привычка."
                )
        return data
