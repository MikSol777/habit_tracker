from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from telegram_bot.models import TelegramProfile

User = get_user_model()


class TelegramLinkAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="p")
        self.client.force_authenticate(user=self.user)

    def test_link_telegram_success(self):
        url = reverse("telegram_bot:telegram-link")
        resp = self.client.post(url, {"chat_id": "123456"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(TelegramProfile.objects.filter(user=self.user, chat_id="123456").exists())

    def test_link_telegram_chat_id_taken_by_other(self):
        other = User.objects.create_user(username="other", password="p")
        TelegramProfile.objects.create(user=other, chat_id="999")
        url = reverse("telegram_bot:telegram-link")
        resp = self.client.post(url, {"chat_id": "999"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_link_telegram_unauthorized(self):
        self.client.force_authenticate(user=None)
        url = reverse("telegram_bot:telegram-link")
        resp = self.client.post(url, {"chat_id": "123"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
