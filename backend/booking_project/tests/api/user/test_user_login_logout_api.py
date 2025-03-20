from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from booking_project.models import User
from booking_project.serializers.user import UserDetailSerializer
from booking_project.tests.api.user.user_setup import UserApiTests


class UserLoginLogoutTests(UserApiTests):
    def test_user_can_login_with_correct_data(self):
        """
        Test if the user can log in and get a token.
        Sends a POST request with valid data and expects a 200 OK response.
        Verifies that the user has received a token and has access to his profile.
        """

        data = {
            "email": "user@example.com",
            "password": "userpassword"
        }

        self.client.cookies.clear()

        response = self.client.post(self.user_login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.cookies.get("access_token"))
        self.assertIsNotNone(response.cookies.get("refresh_token"))
        self.assertNotEqual(response.cookies.get("access_token").value, "")
        self.assertNotEqual(response.cookies.get("refresh_token").value, "")

        """
        An authorized user has access to his profile.
        Send a GET Request and expects a 200 OK response.
        Verifies that the user profile contains correct data.
        """

        user = User.objects.get(email="user@example.com")

        expected_data = UserDetailSerializer(user).data

        new_response = self.client.get(self.user_retrieve_update_delete_url)

        self.assertEqual(new_response.status_code, status.HTTP_200_OK)
        self.assertEqual(new_response.data, expected_data)

    def test_user_logout_correctly(self):
        """
        Test if the user exits correctly and received jwt tokens are deleted
        Sends a POST request and expects a 200 OK response.
        Verifies that cookies have been deleted and the user does not have access to his profile.
        """

        refresh = RefreshToken.for_user(self.user)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.post(self.user_logout_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.cookies.get("access_token").value, "")
        self.assertEqual(response.cookies.get("refresh_token").value, "")

        """
        Unauthorized users cannot access their profile.
        Send a GET Request and expects a 401 UNAUTHORIZED response.
        """

        new_response = self.client.get(self.user_retrieve_update_delete_url)

        self.assertEqual(new_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(new_response.data["detail"], "Authentication credentials were not provided.")

    def test_deleted_user_cannot_login(self):
        """
        Test if a deleted user cannot log in.
        Sends a POST request with login data and expects a 404 NOT FOUND response.
        Verifies that the user does not receive cookies.
        """

        data = {
            "email": "deleteduser@example.com",
            "password": "deleteduserpassword"
        }

        self.client.cookies.clear()

        response = self.client.post(self.user_login_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No User matches the given query.")
        self.assertIsNone(response.cookies.get("access_token"))
        self.assertIsNone(response.cookies.get("refresh_token"))
