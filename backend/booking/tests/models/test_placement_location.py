from django.core.exceptions import ValidationError

from booking.models import PlacementLocation
from booking.tests.models.placement_setup import PlacementSetupTest


class PlacementLocationModelTest(PlacementSetupTest):

    def setUp(self):
        super().setUp()

        self.placement_location = PlacementLocation.objects.create(
            placement=self.placement,
            country="Test Country",
            city="Test city",
            post_code="10405",
            street="Test street",
            house_number="1"
        )

    def test_create_placement_location(self):
        """Test creating a placement location."""

        self.assertIsNotNone(self.placement_location.id)
        self.assertIsNotNone(self.placement_location.placement)
        self.assertEqual(self.placement_location.placement, self.placement)
        self.assertEqual(self.placement_location.country, "Test Country")
        self.assertEqual(self.placement_location.city, "Test city")
        self.assertEqual(self.placement_location.post_code, "10405")
        self.assertEqual(self.placement_location.street, "Test street")
        self.assertEqual(self.placement_location.house_number, "1")

    def test_one_placement_has_one_location(self):
        """Test the one placement cannot have second (or more) location model"""

        new_location = PlacementLocation(
            placement=self.placement,
            country="Test Country",
            city="Test city",
            post_code="10405",
            street="Test street",
            house_number="1"
        )

        with self.assertRaises(ValidationError) as context:
            new_location.full_clean()
        error_message = context.exception.message_dict.get("placement", [])
        self.assertIn("Placement Location with this Placement already exists.", error_message)

    def test_placement_location_cannot_be_created_without_placement(self):
        """Test the placement location cannot be created without placement field."""

        new_location = PlacementLocation(
            placement=None,
            country="Test Country",
            city="Test city",
            post_code="10405",
            street="Test street",
            house_number="1"
        )

        with self.assertRaises(ValidationError) as context:
            new_location.full_clean()
        error_message = context.exception.message_dict.get("placement", [])
        self.assertIn("This field cannot be null.", error_message)

    def test_fields_max_length(self):
        """
        Test the maximal length of the fields: country, city, post_code,
        street, house_number.
        """

        new_location = PlacementLocation(
            placement=self.placement,
            country="A" * 156,
            city="A" * 156,
            post_code="A" * 7,
            street="A" * 156,
            house_number="A" * 31
        )

        with self.assertRaises(ValidationError) as context:
            new_location.full_clean()
        error_message = str(context.exception)
        self.assertIn("country", error_message)
        self.assertIn("city", error_message)
        self.assertIn("post_code", error_message)
        self.assertIn("street", error_message)
        self.assertIn("house_number", error_message)

    def test_post_code_cannot_contain_non_numeric_characters(self):
        """Test the post_code fields can contain only numeric characters"""

        new_location = PlacementLocation(
            placement=self.placement,
            country="Test Country",
            city="Test city",
            post_code="10as5",
            street="Test street",
            house_number="1"
        )

        with self.assertRaises(ValidationError) as context:
            new_location.full_clean()
        error_message = context.exception.message_dict.get("post_code", [])[0]
        self.assertEqual("Invalid postal code.", error_message)
