from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterAPITest(APITestCase):
    def test_register_success(self):
        url = reverse("users:register")
        data = {"username": "newuser", "password": "securepass123"}
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn("id", resp.data)
        self.assertEqual(resp.data["username"], "newuser")
        self.assertNotIn("password", resp.data)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_register_with_email(self):
        url = reverse("users:register")
        data = {"username": "u2", "email": "u2@example.com", "password": "pass12345"}
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(username="u2").email, "u2@example.com")


class TokenAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tokenuser", password="mypass123")

    def test_obtain_token(self):
        url = reverse("users:token_obtain_pair")
        resp = self.client.post(
            url,
            {"username": "tokenuser", "password": "mypass123"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)

    def test_token_wrong_password(self):
        url = reverse("users:token_obtain_pair")
        resp = self.client.post(
            url,
            {"username": "tokenuser", "password": "wrong"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
