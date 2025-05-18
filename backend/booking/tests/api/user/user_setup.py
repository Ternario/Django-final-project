from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from booking.models.user import User

from django.test.utils import override_settings


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class UserApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_create_url = reverse("user-create")

        cls.user_login_url = reverse("user-login")
        cls.user_logout_url = reverse("user-logout")

        cls.user_retrieve_update_delete_url = reverse("user-details")
        cls.user_retrieve_base_detail_url = reverse("user-base-details")

        cls.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            first_name="Admin",
            last_name="Admin",
            username="Admin",
            phone="+1234567899",
            password="adminpassword",
        )

        cls.deleted_user = User.objects.create_user(
            email="deleteduser@example.com",
            first_name="Deleteduser",
            last_name="Deleteduser",
            username="Deleteduser",
            phone="+123456789789076",
            password="deleteduserpassword",
            is_deleted=True,
        )

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            first_name="User",
            last_name="User",
            username="FirstUser",
            phone="+123456789",
            password="userpassword",
        )

        self.client = APIClient()

        refresh = RefreshToken.for_user(self.user)
        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)
