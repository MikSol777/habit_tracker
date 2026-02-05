from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from habits.models import Habit
from habits.validators import validate_habit

User = get_user_model()


class HabitModelTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="testpass123")

    def test_create_habit(self):
        habit = Habit.objects.create(
            user=self.user,
            action="Проверять почту",
            place="Офис",
            time="08:00:00",
            duration=60,
            is_pleasant=False,
        )
        self.assertEqual(habit.user.username, "test")
        self.assertEqual(habit.duration, 60)
        self.assertEqual(habit.frequency, 1)


class HabitValidatorTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="p")
        self.pleasant = Habit.objects.create(
            user=self.user,
            action="Ванна",
            place="Дом",
            time="21:00:00",
            duration=30,
            is_pleasant=True,
        )
        self.useful = Habit.objects.create(
            user=self.user,
            action="Прогулка",
            place="Парк",
            time="19:00:00",
            duration=60,
            is_pleasant=False,
        )

    def test_reward_and_related_forbidden(self):
        with self.assertRaises(ValidationError):
            validate_habit({"reward": "десерт", "related_habit": self.pleasant})

    def test_duration_over_120_forbidden(self):
        with self.assertRaises(ValidationError):
            validate_habit({"duration": 121})

    def test_duration_zero_forbidden(self):
        with self.assertRaises(ValidationError):
            validate_habit({"duration": 0})

    def test_frequency_over_7_forbidden(self):
        with self.assertRaises(ValidationError):
            validate_habit({"frequency": 8})

    def test_frequency_zero_forbidden(self):
        with self.assertRaises(ValidationError):
            validate_habit({"frequency": 0})

    def test_related_must_be_pleasant(self):
        with self.assertRaises(ValidationError):
            validate_habit({"related_habit": self.useful})

    def test_pleasant_cannot_have_reward(self):
        with self.assertRaises(ValidationError):
            validate_habit({"is_pleasant": True, "reward": "что-то"})

    def test_pleasant_cannot_have_related(self):
        with self.assertRaises(ValidationError):
            validate_habit({"is_pleasant": True, "related_habit": self.pleasant})

    def test_valid_useful_habit_with_reward(self):
        validate_habit({"reward": "десерт", "duration": 60, "frequency": 1})

    def test_valid_useful_habit_with_related(self):
        validate_habit({"related_habit": self.pleasant, "duration": 60, "frequency": 1})


class HabitAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="pass123")
        self.other = User.objects.create_user(username="user2", password="pass123")
        self.client.force_authenticate(user=self.user)

    def test_list_own_habits(self):
        Habit.objects.create(
            user=self.user,
            action="Читать",
            place="Кровать",
            time="22:00:00",
            duration=30,
        )
        url = reverse("habit-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 1)
        self.assertEqual(resp.data["results"][0]["action"], "Читать")

    def test_list_paginated(self):
        for i in range(7):
            Habit.objects.create(
                user=self.user,
                action=f"Привычка {i}",
                place="Место",
                time="08:00:00",
                duration=60,
            )
        url = reverse("habit-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 5)
        self.assertIsNotNone(resp.data.get("next"))

    def test_create_habit(self):
        url = reverse("habit-list")
        data = {
            "action": "Пить воду",
            "place": "Кухня",
            "time": "09:00:00",
            "duration": 60,
            "frequency": 1,
        }
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["action"], "Пить воду")
        self.assertEqual(resp.data["user"], self.user.id)
        self.assertEqual(Habit.objects.filter(user=self.user).count(), 1)

    def test_create_habit_invalid_duration_rejected(self):
        url = reverse("habit-list")
        resp = self.client.post(
            url,
            {"action": "X", "place": "Y", "time": "09:00:00", "duration": 150},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_habit_unauthorized(self):
        self.client.force_authenticate(user=None)
        url = reverse("habit-list")
        resp = self.client.post(
            url,
            {
                "action": "X",
                "place": "Y",
                "time": "09:00:00",
                "duration": 60,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_own_habit(self):
        habit = Habit.objects.create(
            user=self.user,
            action="Старое",
            place="Место",
            time="08:00:00",
            duration=60,
        )
        url = reverse("habit-detail", args=[habit.pk])
        resp = self.client.patch(url, {"action": "Новое"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        habit.refresh_from_db()
        self.assertEqual(habit.action, "Новое")

    def test_delete_own_habit(self):
        habit = Habit.objects.create(
            user=self.user,
            action="Удалить",
            place="Место",
            time="08:00:00",
            duration=60,
        )
        url = reverse("habit-detail", args=[habit.pk])
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Habit.objects.filter(pk=habit.pk).exists())

    def test_cannot_see_other_habit(self):
        habit = Habit.objects.create(
            user=self.other,
            action="Чужая",
            place="Место",
            time="08:00:00",
            duration=60,
        )
        url = reverse("habit-detail", args=[habit.pk])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


class HabitTasksTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="p")

    def test_send_telegram_reminder_no_token(self):
        from habits.tasks import send_telegram_reminder
        with self.settings():
            send_telegram_reminder("123", "test message")

    def test_send_habit_reminders_runs(self):
        from habits.tasks import send_habit_reminders
        send_habit_reminders()


class PublicHabitAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="p")
        Habit.objects.create(
            user=self.user,
            action="Публичная",
            place="Парк",
            time="09:00:00",
            duration=60,
            is_public=True,
        )
        Habit.objects.create(
            user=self.user,
            action="Приватная",
            place="Дом",
            time="10:00:00",
            duration=30,
            is_public=False,
        )

    def test_public_list_without_auth(self):
        self.client.force_authenticate(user=None)
        url = reverse("public-habits")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        actions = [h["action"] for h in resp.data["results"]]
        self.assertIn("Публичная", actions)
        self.assertNotIn("Приватная", actions)
