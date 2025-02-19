from rest_framework import status
from booking_project.models.user import User
from booking_project.tests.api.user.user_setup import UserApiTests


class UserCreateTests(UserApiTests):
    def test_user_can_create_account(self):
        """
        Test if unregistered user can create an Account.
        Sends a POST request with valid data and expects a 201 CREATED response.
        Verifies that the user count increases and the new User has the correct email.
        """

        data = {
            "email": "newuser@example.com",
            "first_name": "newuser",
            "last_name": "newuser",
            "username": "newuser",
            "phone": "+1112223344",
            "password": "newuserpassword",
            "re_password": "newuserpassword"
        }

        response = self.client.post(self.user_create_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "User successfully created.")
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.last().email, "newuser@example.com")

    def test_user_can_create_account_without_username(self):
        """
        Test if unregistered user can create an Account without Username.
        Sends a POST request with valid data where the username field is empty and expects a 201 CREATED response.
        Verifies that the user count increases and the new User has the correct email.
        """

        data = {
            "email": "newuser@example.com",
            "first_name": "newuser",
            "last_name": "newuser",
            "username": "",
            "phone": "+1112223344",
            "password": "newuserpassword",
            "re_password": "newuserpassword"
        }

        response = self.client.post(self.user_create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "User successfully created.")
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(User.objects.last().email, "newuser@example.com")

    def test_user_cannot_create_account_with_existing_email(self):
        """
        Test if unregistered user cannot create an Account with an existing Email.
        Sends a POST request with valid data but existing Email and expects a 400 BAD REQUEST response.
        Verifies that the number of users has not increased.
        """

        data = {
            "email": "user@example.com",
            "first_name": "newuser",
            "last_name": "newuser",
            "username": "newuser",
            "phone": "+1112223344",
            "password": "newuserpassword",
            "re_password": "newuserpassword"
        }

        response = self.client.post(self.user_create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], "user with this Email already exists.")
        self.assertEqual(User.objects.count(), 2)

    def test_user_cannot_create_account_with_existing_username(self):
        """
        Test if unregistered user cannot create an Account with an existing Username.
        Sends a POST request with valid data but existing Username and expects a 400 BAD REQUEST response.
        Verifies that the number of users has not increased.
        """

        data = {
            "email": "newuser@example.com",
            "first_name": "newuser",
            "last_name": "newuser",
            "username": "FirstUser",
            "phone": "+1112223344",
            "password": "newuserpassword",
            "re_password": "newuserpassword"
        }

        response = self.client.post(self.user_create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["username"][0], "user with this Username already exists.")
        self.assertEqual(User.objects.count(), 2)

    def test_user_cannot_create_account_with_existing_phone_number(self):
        """
        Test if unregistered user cannot create an Account with an existing Phone Number.
        Sends a POST request with valid data but existing Phone Number and expects a 400 BAD REQUEST response.
        Verifies that the number of users has not increased.
        """

        data = {
            "email": "newuser@example.com",
            "first_name": "newuser",
            "last_name": "newuser",
            "username": "newuser",
            "phone": "+123456789",
            "password": "newuserpassword",
            "re_password": "newuserpassword"
        }

        response = self.client.post(self.user_create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["phone"][0], "user with this Phone number already exists.")
        self.assertEqual(User.objects.count(), 2)

    def test_user_cannot_create_account_without_email(self):
        """
        Test if unregistered user cannot create an Account without Email.
        Sends a POST request with data where the email field is empty and expects a 400 BAD REQUEST response.
        Verifies that the number of users has not increased.
        """

        data = {
            "email": "",
            "first_name": "newuser",
            "last_name": "newuser",
            "username": "newuser",
            "phone": "+1112223344",
            "password": "newuserpassword",
            "re_password": "newuserpassword"
        }

        response = self.client.post(self.user_create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["email"][0], "This field may not be blank.")
        self.assertEqual(User.objects.count(), 2)

    def test_user_cannot_create_account_without_first_name(self):
        """
        Test if unregistered user cannot create an Account without First Name.
        Sends a POST request with data where the first_name field is empty and expects a 400 BAD REQUEST response.
        Verifies that the number of users has not increased.
        """

        data = {
            "email": "newuser@example.com",
            "first_name": "",
            "last_name": "newuser",
            "username": "newuser",
            "phone": "+1112223344",
            "password": "newuserpassword",
            "re_password": "newuserpassword"
        }

        response = self.client.post(self.user_create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["first_name"][0], "This field may not be blank.")
        self.assertEqual(User.objects.count(), 2)

    def test_user_cannot_create_account_without_last_name(self):
        """
        Test if unregistered user cannot create an Account without Last Name.
        Sends a POST request with data where the last_name field is empty and expects a 400 BAD REQUEST response.
        Verifies that the number of users has not increased.
        """

        data = {
            "email": "newuser@example.com",
            "first_name": "newuser",
            "last_name": "",
            "username": "newuser",
            "phone": "+1112223344",
            "password": "newuserpassword",
            "re_password": "newuserpassword"
        }

        response = self.client.post(self.user_create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["last_name"][0], "This field may not be blank.")
        self.assertEqual(User.objects.count(), 2)

    def test_user_cannot_create_account_without_phone_number(self):
        """
        Test if unregistered user cannot create an Account without Phone Number.
        Sends a POST request with data where the phone field is empty and expects a 400 BAD REQUEST response.
        Verifies that the number of users has not increased.
        """

        data = {
            "email": "newuser@example.com",
            "first_name": "newuser",
            "last_name": "newuser",
            "username": "newuser",
            "phone": "",
            "password": "newuserpassword",
            "re_password": "newuserpassword"
        }

        response = self.client.post(self.user_create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["phone"][0], "This field may not be blank.")
        self.assertEqual(User.objects.count(), 2)

    def test_user_cannot_create_account_without_password(self):
        """
        Test if unregistered user cannot create an Account without Password.
        Sends a POST request with data where the password field is empty and expects a 400 BAD REQUEST response.
        Verifies that the number of users has not increased.
        """

        data = {
            "email": "newuser@example.com",
            "first_name": "newuser",
            "last_name": "newuser",
            "username": "newuser",
            "phone": "+1112223344",
            "password": "",
            "re_password": "newuserpassword"
        }

        response = self.client.post(self.user_create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["password"][0], "This field may not be blank.")
        self.assertEqual(User.objects.count(), 2)

    def test_user_cannot_create_account_without_re_password(self):
        """
        Test if unregistered user cannot create an Account without repeated Password.
        Sends a POST request with data where the re_password field is empty and expects a 400 BAD REQUEST response.
        Verifies that the number of users has not increased.
        """

        data = {
            "email": "newuser@example.com",
            "first_name": "newuser",
            "last_name": "newuser",
            "username": "newuser",
            "phone": "+1112223344",
            "password": "newuserpassword",
            "re_password": ""
        }

        response = self.client.post(self.user_create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["re_password"][0], "This field may not be blank.")
        self.assertEqual(User.objects.count(), 2)

    def test_user_cannot_create_account_with_wrong_passwords(self):
        """
        Test if unregistered user cannot create an Account when passwords don't match.
        Sends a POST request with data in which the password and re_password fields don't match
        and expects a 400 BAD REQUEST response.
        Verifies that the number of users has not increased.
        """

        data = {
            "email": "newuser@example.com",
            "first_name": "newuser",
            "last_name": "newuser",
            "username": "newuser",
            "phone": "+1112223344",
            "password": "newuserpassword",
            "re_password": "wrongpassword"
        }

        response = self.client.post(self.user_create_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["password"][0], "Passwords don't match")
        self.assertEqual(User.objects.count(), 2)
