from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from booking_project.models.user import User


class UserApiTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            first_name="Admin",
            last_name="Admin",
            username="Admin",
            phone="+1234567899",
            password="adminpassword",
        )

        self.user = User.objects.create_user(
            email="user@example.com",
            first_name="User",
            last_name="User",
            username="FirstUser",
            phone="+123456789",
            password="userpassword",
        )

        self.deleted_user = User.objects.create_user(
            email="deleteduser@example.com",
            first_name="Deleteduser",
            last_name="Deleteduser",
            username="Deleteduser",
            phone="+123456789789076",
            password="deleteduserpassword",
            is_deleted=True,
        )

        self.client = APIClient()

        refresh = RefreshToken.for_user(self.user)
        self.client.cookies['access_token'] = str(refresh.access_token)
        self.client.cookies['refresh_token'] = str(refresh)

        self.user_create_url = reverse("user-create")

        self.user_login_url = reverse("user-login")
        self.user_logout_url = reverse("user-logout")

        self.user_retrieve_update_delete_url = reverse("user-details")
        self.user_retrieve_base_detail_url = reverse("user-base-details")
