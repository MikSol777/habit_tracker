from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Habit
from .serializers import HabitSerializer
from .pagination import HabitPagination


class HabitViewSet(ModelViewSet):
    """CRUD привычек текущего пользователя. Доступ только к своим привычкам."""

    serializer_class = HabitSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = HabitPagination

    def get_queryset(self):
        return (
            Habit.objects.filter(user=self.request.user)
            .select_related("related_habit")
            .order_by("-created_at")
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PublicHabitListView(ListAPIView):
    """Список публичных привычек (только чтение)."""

    queryset = (
        Habit.objects.filter(is_public=True)
        .select_related("user", "related_habit")
        .order_by("-created_at")
    )
    serializer_class = HabitSerializer
    permission_classes = (AllowAny,)
    pagination_class = HabitPagination
