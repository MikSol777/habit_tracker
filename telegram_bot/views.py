from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TelegramProfile
from .serializers import TelegramProfileSerializer


class TelegramLinkView(APIView):
    """Привязка Telegram chat_id к текущему пользователю для напоминаний."""

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = TelegramProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat_id = serializer.validated_data["chat_id"]
        existing = TelegramProfile.objects.filter(chat_id=chat_id).exclude(user=request.user).first()
        if existing:
            return Response(
                {"detail": "Этот Telegram уже привязан к другому аккаунту."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        TelegramProfile.objects.update_or_create(
            user=request.user,
            defaults={"chat_id": chat_id},
        )
        return Response(
            {"detail": "Telegram успешно привязан для напоминаний."},
            status=status.HTTP_200_OK,
        )
