from rest_framework import status

from booking_project.models import User
from booking_project.serializers.user import UserDetailSerializer, UserBaseDetailSerializer
from booking_project.tests.api.user.user_setup import UserApiTests


class UserRetrieveUpdateDeleteTests(UserApiTests):

    def test_user_retrieve_his_profile(self):
        """
        Test if the user receives his profile.
        Send a GET Request and expects a 200 OK response.
        Verifies that the user profile contains correct data.
        """

        user = User.objects.get(email="user@example.com")

        expected_data = UserDetailSerializer(user).data

        response = self.client.get(self.user_retrieve_update_delete_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_user_retrieve_his_profile_base_detail(self):
        """
        Test if the user is retrieving his basic profile data.
        Send a GET Request and expects a 200 OK response.
        Verifies that the user profile base data contains correct data.
        """

        user = User.objects.get(email="user@example.com")

        expected_data = UserBaseDetailSerializer(user).data

        response = self.client.get(self.user_retrieve_base_detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, expected_data)

    def test_user_can_update_profile(self):
        """
        Test if the user can update his profile.
        Send a PUT Request with valid data and expects a 200 OK response.
        Verifies that the user profile is updated correctly.
        """

        data = {
            "email": "updateduser@example.com",
            "first_name": "updateduser",
            "last_name": "updateduser",
            "username": "updateduser",
            "phone": "+5986785643",
            "date_of_birth": "01-02-2020"
        }

        response = self.client.put(self.user_retrieve_update_delete_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "updateduser@example.com")
        self.assertEqual(response.data["first_name"], "updateduser")
        self.assertEqual(response.data["last_name"], "updateduser")
        self.assertEqual(response.data["username"], "updateduser")
        self.assertEqual(response.data["phone"], "+5986785643")

    def test_user_cannot_update_profile_existing_email(self):
        """
        Test if the user cannot update his profile with an existing Email.
        Send a PUT Request with valid data but existing Email and expects a 400 BAD REQUEST response.
        Verifies that the user's profile has not been updated.
        """

        data = {
            "email": "admin@example.com",
            "first_name": "updateduser",
            "last_name": "updateduser",
            "username": "updateduser",
            "phone": "+5986785643",
        }

        response = self.client.put(self.user_retrieve_update_delete_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], "user with this Email already exists.")
        self.assertEqual(User.objects.last().email, "user@example.com")
        self.assertEqual(User.objects.last().first_name, "User")

    def test_user_cannot_update_profile_existing_username(self):
        """
        Test if the user cannot update his profile with an existing Username.
        Send a PUT Request with valid data but existing Username and expects a 400 BAD REQUEST response.
        Verifies that the user's profile has not been updated.
        """

        data = {
            "email": "updateduser@example.com",
            "first_name": "updateduser",
            "last_name": "updateduser",
            "username": "Admin",
            "phone": "+5986785643",
        }

        response = self.client.put(self.user_retrieve_update_delete_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["username"][0], "user with this Username already exists.")
        self.assertEqual(User.objects.last().email, "user@example.com")
        self.assertEqual(User.objects.last().username, "FirstUser")

    def test_user_cannot_update_profile_existing_phone_number(self):
        """
        Test if the user cannot update his profile with an existing Phone Number.
        Send a PUT Request with valid data but existing Phone Number and expects a 400 BAD REQUEST response.
        Verifies that the user's profile has not been updated.
        """

        data = {
            "email": "updateduser@example.com",
            "first_name": "updateduser",
            "last_name": "updateduser",
            "username": "FirstUser",
            "phone": "+1234567899",
        }

        response = self.client.put(self.user_retrieve_update_delete_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["phone"][0], "user with this Phone number already exists.")
        self.assertEqual(User.objects.last().email, "user@example.com")
        self.assertEqual(User.objects.last().phone, "+123456789")

    def test_user_can_partially_update_profile(self):
        """
        Test if the user can partially update his profile.
        Send a PATCH Request with valid data and expects a 200 OK response.
        Verifies that the updated user profile fields have been changed correctly.
        """

        data = {
            "email": "partialupdateduser@example.com",
            "first_name": "partialupdateduser",
            "username": "partialupdateduser",
        }

        response = self.client.patch(self.user_retrieve_update_delete_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "partialupdateduser@example.com")
        self.assertEqual(response.data["first_name"], "partialupdateduser")
        self.assertEqual(response.data["username"], "partialupdateduser")

    def test_user_cannot_update_profile_throw_base_detail_endpoint(self):
        """
        Test if the user cannot update his profile throw base detail endpoint.
        Send a PUT Request with valid data to the base detail endpoint and expects a 405 METHOD NOT ALLOWED response.
        Verifies that the user's profile has not been updated.
        """

        data = {
            "email": "updateduser@example.com",
            "first_name": "updateduser",
            "last_name": "updateduser",
            "username": "updateduser"
        }

        response = self.client.put(self.user_retrieve_base_detail_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data["detail"], "Method \"PUT\" not allowed.")
        self.assertEqual(User.objects.last().email, "user@example.com")
        self.assertEqual(User.objects.last().first_name, "User")
        self.assertEqual(User.objects.last().last_name, "User")
        self.assertEqual(User.objects.last().username, "FirstUser")

    def test_user_cannot_partially_update_profile_throw_base_detail_endpoint(self):
        """
        Test if the user cannot partially update his profile throw base detail endpoint.
        Send a PATCH Request with valid data to the base detail endpoint and expects a 405 METHOD NOT ALLOWED response.
        Verifies that the user's profile has not been updated.
        """

        data = {
            "email": "updateduser@example.com",
            "first_name": "updateduser",
        }

        response = self.client.patch(self.user_retrieve_base_detail_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data["detail"], "Method \"PATCH\" not allowed.")
        self.assertEqual(User.objects.last().email, "user@example.com")
        self.assertEqual(User.objects.last().first_name, "User")

    def test_unauthorized_user_cannot_update_profile(self):
        """
        Test if the unauthorized user cannot update his profile.
        Send a PUT Request with data and expects a 401 UNAUTHORIZED response.
        Verifies that the user profile has not been updated.
        """

        data = {
            "email": "updateduser@example.com",
            "first_name": "updateduser",
            "last_name": "updateduser",
            "username": "updateduser",
            "phone": "+5986785643",
        }

        self.client.cookies.clear()

        response = self.client.put(self.user_retrieve_update_delete_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")
        self.assertEqual(User.objects.last().email, "user@example.com")
        self.assertEqual(User.objects.last().first_name, "User")
        self.assertEqual(User.objects.last().last_name, "User")
        self.assertEqual(User.objects.last().username, "FirstUser")
        self.assertEqual(User.objects.last().phone, "+123456789")

    def test_user_can_delete_his_profile(self):
        """
        Test if user can delete his profile.
        Send a DELETE request and expects a 204 NO CONTENT response.
        Verifies that the user does not exist.
        """

        response = self.client.delete(self.user_retrieve_update_delete_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.all_objects.count(), 3)

    def test_unauthorized_user_cannot_delete_profile(self):
        """
        Test if the unauthorized user cannot delete the profile.
        Send a DELETE Request and expects a 401 UNAUTHORIZED response.
        Verifies that the user profile has not been deleted.
        """

        self.client.cookies.clear()

        response = self.client.delete(self.user_retrieve_update_delete_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(User.objects.count(), 2)
