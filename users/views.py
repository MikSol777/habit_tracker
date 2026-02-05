from rest_framework import generics
from rest_framework.permissions import AllowAny

from .serializers import UserRegistrationSerializer


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя."""

    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer
