from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthAndProfileTests(APITestCase):
    def setUp(self):
        self.register_url = reverse("accounts:register")
        self.login_url = reverse("accounts:token_obtain_pair")
        self.me_url = reverse("accounts:current_user")
        self.profile_url = reverse("accounts:profile_update")

        self.user_data = {
            "username": "testtrader",
            "email": "trader@example.com",
            "password": "StrongPassword123!",
            "password2": "StrongPassword123!",
        }

    def test_user_registration_and_auto_profile(self):
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["username"], "testtrader")

        user = User.objects.get(username="testtrader")
        self.assertIsNotNone(user.profile)
        self.assertEqual(user.profile.default_exchange, "NSE")

    def test_user_login(self):
        User.objects.create_user(
            username="testtrader",
            email="trader@example.com",
            password="StrongPassword123!",
        )

        login_data = {
            "username": "testtrader",
            "password": "StrongPassword123!",
        }
        response = self.client.post(self.login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_get_and_update_profile(self):
        user = User.objects.create_user(
            username="testtrader",
            email="trader@example.com",
            password="StrongPassword123!",
        )
        self.client.force_authenticate(user=user)

        # GET profile
        me_resp = self.client.get(self.me_url)
        self.assertEqual(me_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(me_resp.data["username"], "testtrader")

        # PATCH profile
        patch_data = {
            "telegram_chat_id": "123456789",
            "telegram_alerts_enabled": True,
            "default_exchange": "MCX",
            "default_product": "FUTURES",
            "favorite_symbols": ["GOLD", "CRUDEOIL"],
        }
        profile_resp = self.client.patch(self.profile_url, patch_data, format="json")
        self.assertEqual(profile_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_resp.data["telegram_chat_id"], "123456789")
        self.assertTrue(profile_resp.data["telegram_alerts_enabled"])
        self.assertEqual(profile_resp.data["default_exchange"], "MCX")
        self.assertEqual(profile_resp.data["favorite_symbols"], ["GOLD", "CRUDEOIL"])

