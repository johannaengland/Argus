from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from argus.auth.factories import AdminUserFactory, PersonUserFactory

from . import assemble_token_auth_kwarg, expire_token


User = get_user_model()


class AuthTokenAPITests(APITestCase):
    def setUp(self):
        self.superuser1_password = "best_admin#1"
        self.superuser1 = AdminUserFactory(username="superuser1", password=self.superuser1_password)

        self.normal_user1_password = "12345"
        self.normal_user1 = PersonUserFactory(username="normal_user1", password=self.normal_user1_password)

        self.superuser1_client = APIClient()
        self.superuser1_token = Token.objects.create(user=self.superuser1)
        self.superuser1_client.credentials(**assemble_token_auth_kwarg(self.superuser1_token.key))

        self.normal_user1_client = APIClient()
        self.normal_user1_token = Token.objects.create(user=self.normal_user1)
        self.normal_user1_client.credentials(**assemble_token_auth_kwarg(self.normal_user1_token.key))

    def _successfully_get_auth_token(self, user: User, user_password: str, client: APIClient):
        auth_token_path = reverse("v1:api-token-auth")
        response = client.post(auth_token_path, {"username": user.username, "password": user_password})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response

    def test_get_auth_token_always_replaces_old_token(self):
        def assert_token_is_replaced(user: User, user_password: str, old_token: Token, client: APIClient):
            old_token_key = old_token.key

            response = self._successfully_get_auth_token(user, user_password, client)
            new_token_key = response.data["token"]

            self.assertNotEqual(new_token_key, old_token_key)
            with self.assertRaises(Token.DoesNotExist):
                old_token.refresh_from_db()
            user.refresh_from_db()
            self.assertEqual(new_token_key, user.auth_token.key)

        assert_token_is_replaced(
            self.normal_user1, self.normal_user1_password, self.normal_user1_token, self.normal_user1_client
        )
        assert_token_is_replaced(
            self.superuser1, self.superuser1_password, self.superuser1_token, self.superuser1_client
        )

    def test_auth_token_expires_and_is_deleted(self):
        some_auth_required_path = reverse("v1:auth:current-user")

        def assert_token_expires_and_is_deleted(user: User, token: Token, client: APIClient):
            self.assertEqual(client.get(some_auth_required_path).status_code, status.HTTP_200_OK)

            expire_token(token)

            self.assertEqual(client.get(some_auth_required_path).status_code, status.HTTP_401_UNAUTHORIZED)
            user.refresh_from_db()
            self.assertFalse(hasattr(user, "auth_token"))
            with self.assertRaises(Token.DoesNotExist):
                token.refresh_from_db()

        assert_token_expires_and_is_deleted(self.normal_user1, self.normal_user1_token, self.normal_user1_client)
        assert_token_expires_and_is_deleted(self.superuser1, self.superuser1_token, self.superuser1_client)

    def test_get_current_user_returns_correct_user(self):
        current_user_path = reverse("v1:auth:current-user")

        response = self.superuser1_client.get(current_user_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.superuser1.username)

        response = self.normal_user1_client.get(current_user_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.normal_user1.username)

    def test_get_user_returns_the_correct_fields(self):
        def user_path(user: User):
            return reverse("v1:auth:user", args=[user.pk])

        def assert_correct_fields_for_user(user: User):
            response = self.normal_user1_client.get(user_path(user))
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            response_data = response.data
            self.assertEqual(len(response_data), 4)
            self.assertEqual(response_data["username"], user.username)
            self.assertIn("first_name", response_data)
            self.assertIn("last_name", response_data)
            self.assertIn("email", response_data)

        assert_correct_fields_for_user(self.normal_user1)
        assert_correct_fields_for_user(self.superuser1)

    def test_refresh_token_returns_correct_new_token(self):
        auth_token_path = reverse("v2:auth:refresh-token")
        response = self.normal_user1_client.post(auth_token_path)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data["token"], self.normal_user1_token.key)
        self.assertEqual(response.data["token"], Token.objects.get(user=self.normal_user1).key)
