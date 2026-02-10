from django.test import TestCase
from django.core.exceptions import ValidationError

from properties.models.user import User


class UserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = User.objects.create(
            email="admin@example.com",
            first_name="Admin",
            last_name="Admin",
            username="Admin",
            phone="+123456789"
        )

    def test_create_user(self):
        """Test creating a user."""

        self.assertIsNotNone(self.user.id)

        self.assertIsNone(self.user.date_of_birth)

        self.assertEqual(self.user.is_landlord, False)
        self.assertEqual(self.user.is_verified, False)
        self.assertEqual(self.user.email, "admin@example.com")
        self.assertEqual(self.user.first_name, "Admin")
        self.assertEqual(self.user.last_name, "Admin")
        self.assertEqual(self.user.username, "Admin")
        self.assertEqual(self.user.phone, "+123456789")

    def test_model_cannot_be_created_without_required_fields(self):
        """Test user model cannot  be created without email, first_name, last_name or phone field."""

        new_user = User(
            email=None,
            first_name=None,
            last_name=None,
            username="Example",
            phone=None
        )

        with self.assertRaises(ValidationError) as context:
            new_user.full_clean()
        error_message = str(context.exception)
        self.assertIn("email", error_message)
        self.assertIn("first_name", error_message)
        self.assertIn("last_name", error_message)
        self.assertIn("phone", error_message)

    def test_email_uniqueness(self):
        """Check email uniqueness."""

        new_user = User(
            email="admin@example.com",
            first_name="Example",
            last_name="Example",
            username="Example",
            phone="+123456789"
        )

        with self.assertRaises(ValidationError) as context:
            new_user.full_clean()
        error_message = context.exception.message_dict.get("email", [])
        self.assertIn("User with this Email already exists.", error_message)

    def test_username_uniqueness(self):
        """Check username uniqueness"""

        new_user = User(
            email="user@example.com",
            first_name="Example",
            last_name="Example",
            username="Admin",
            phone="+123456789"
        )

        with self.assertRaises(ValidationError) as context:
            new_user.full_clean()
        error_message = context.exception.message_dict.get("username", [])
        self.assertIn("User with this Username already exists.", error_message)

    def test_phone_uniqueness(self):
        """Check phone uniqueness."""

        new_user = User(
            email="user@example.com",
            first_name="Example",
            last_name="Example",
            username="Example",
            phone="+123456789"
        )

        with self.assertRaises(ValidationError) as context:
            new_user.full_clean()
        error_message = context.exception.message_dict.get("phone", [])
        self.assertIn("User with this Phone number already exists.", error_message)

    def test_fields_max_length(self):
        """Test the maximum length of the fields first_name, last_name, username, phone."""

        new_user = User(
            email="user@example.com",
            first_name="A" * 156,
            last_name="A" * 156,
            username="A" * 36,
            phone="+1" * 21,
        )

        with self.assertRaises(ValidationError) as context:
            new_user.full_clean()
        error_message = str(context.exception)
        self.assertIn("first_name", error_message)
        self.assertIn("last_name", error_message)
        self.assertIn("username", error_message)
        self.assertIn("phone", error_message)

    def test_phone_min_length(self):
        """Test the minimal length of the field phone."""

        new_user = User(
            email="user@example.com",
            first_name="Example",
            last_name="Example",
            username="Example",
            phone=f"+{"1" * 5}",
        )

        with self.assertRaises(ValidationError) as context:
            new_user.full_clean()
        error_message = context.exception.message_dict.get("phone", [])
        self.assertIn("Ensure this value has at least 7 characters (it has 6).", error_message)

    def test_invalid_email(self):
        """Test that the invalid email causes a ValidationError."""

        new_user = User(
            email="user-example.com",
            first_name="Example",
            last_name="Example",
            username="Example",
            phone="+123456789"
        )

        with self.assertRaises(ValidationError) as context:
            new_user.full_clean()

        error_messages = context.exception.message_dict.get('email', [])
        self.assertIn("Enter a valid email address.", error_messages)
