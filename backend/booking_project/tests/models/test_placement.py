from django.core.exceptions import ValidationError

from booking_project.models import Placement
from booking_project.tests.models.placement_setup import PlacementSetupTest


class PlacementModelTest(PlacementSetupTest):

    def test_create_placement(self):
        """Test creating a placement."""

        self.assertIsNotNone(self.placement.id)
        self.assertIsNotNone(self.placement.owner)
        self.assertIsNotNone(self.placement.category)
        self.assertEqual(self.placement.owner, self.user)
        self.assertEqual(self.placement.category, self.category)
        self.assertEqual(self.placement.title, "Hotel by User")
        self.assertEqual(self.placement.description, "A" * 50)
        self.assertEqual(self.placement.price, 250)
        self.assertEqual(self.placement.number_of_rooms, 2)
        self.assertEqual(self.placement.placement_area, 43.5)
        self.assertEqual(self.placement.total_beds, 3)
        self.assertEqual(self.placement.single_bed, 2)
        self.assertEqual(self.placement.double_bed, 1)
        self.assertEqual(self.placement.is_active, True)

    def test_title_uniqueness(self):
        """Test title uniqueness."""

        new_placement = Placement(
            owner=self.user,
            category=self.category,
            title="Hotel by User",
            description="A" * 55,
            price=150,
            number_of_rooms=1,
            placement_area=33.5,
            total_beds=1,
            single_bed=2,
            double_bed=1,
        )

        with self.assertRaises(ValidationError) as context:
            new_placement.full_clean()
        error_message = context.exception.message_dict.get("title", [])
        self.assertIn("Placement with this Apartments title already exists.", error_message)

    def test_placement_cannot_be_created_without_owner(self):
        """Test the placement cannot be created without owner user."""

        new_placement = Placement(
            owner=None,
            category=self.category,
            title="Test Hotel by User",
            description="A" * 50,
            price=250,
            number_of_rooms=2,
            placement_area=43.5,
            total_beds=3,
            single_bed=2,
            double_bed=1,
        )

        with self.assertRaises(ValidationError) as context:
            new_placement.full_clean()
        error_message = context.exception.message_dict.get("owner", [])
        self.assertIn("This field cannot be null.", error_message)

    def test_placement_cannot_be_created_without_category(self):
        """Test the placement cannot be created without category."""

        new_placement = Placement(
            owner=self.user,
            category=None,
            title="Test Hotel by User",
            description="A" * 50,
            price=250,
            number_of_rooms=2,
            placement_area=43.5,
            total_beds=3,
            single_bed=2,
            double_bed=1,
        )

        with self.assertRaises(ValidationError) as context:
            new_placement.full_clean()
        error_message = context.exception.message_dict.get("category", [])
        self.assertIn("This field cannot be null.", error_message)

    def test_fields_max_length_or_max_value(self):
        """
        Test the maximal length or value of the fields: title, description, price,
        number_of_rooms, placement_area, number_of_beds,single_bed, double_bed.
        """

        new_placement = Placement(
            owner=self.user,
            category=self.category,
            title="A" * 256,
            description="A" * 2001,
            price=100000,
            number_of_rooms=7,
            placement_area=1000,
            total_beds=16,
            single_bed=16,
            double_bed=16,
        )

        with self.assertRaises(ValidationError) as context:
            new_placement.full_clean()
        error_message = str(context.exception)
        self.assertIn("title", error_message)
        self.assertIn("description", error_message)
        self.assertIn("price", error_message)
        self.assertIn("number_of_rooms", error_message)
        self.assertIn("placement_area", error_message)
        self.assertIn("total_beds", error_message)
        self.assertIn("single_bed", error_message)
        self.assertIn("double_bed", error_message)

    def test_fields_min_length_or_min_value(self):
        """
        Test the minimal length or value of the fields: description, price,
        number_of_rooms, placement_area, number_of_beds.
        """
        new_placement = Placement(
            owner=self.user,
            category=self.category,
            title="Test Hotel by User",
            description="A" * 39,
            price=9.50,
            number_of_rooms=0,
            placement_area=14.99,
            total_beds=0,
            single_bed=-1,
            double_bed=-1,
        )

        with self.assertRaises(ValidationError) as context:
            new_placement.full_clean()
        error_message = str(context.exception)
        self.assertIn("description", error_message)
        self.assertIn("price", error_message)
        self.assertIn("number_of_rooms", error_message)
        self.assertIn("placement_area", error_message)
        self.assertIn("total_beds", error_message)
        self.assertIn("single_bed", error_message)
        self.assertIn("double_bed", error_message)

    def test_both_bed_fields_cannot_be_zero(self):
        """
        Test the both bed fields cannot be zero.
        """

        new_placement = Placement(
            owner=self.user,
            category=self.category,
            title="Test Hotel by User",
            description="A" * 50,
            price=250,
            number_of_rooms=2,
            placement_area=43.5,
            total_beds=3,
            single_bed=0,
            double_bed=0,
        )

        with self.assertRaises(ValidationError) as context:
            new_placement.full_clean()
        error_message = context.exception.message_dict.get('__all__', [])
        self.assertIn("Constraint “Both bed fields can't be zero.” is violated.", error_message)

    def test_both_bed_fields_cannot_exceed_total_beds(self):
        """
        Test the both bed fields cannot exceed total_beds fields.
        """

        new_placement = Placement(
            owner=self.user,
            category=self.category,
            title="Test Hotel by User",
            description="A" * 50,
            price=250,
            number_of_rooms=2,
            placement_area=43.5,
            total_beds=3,
            single_bed=3,
            double_bed=3,
        )

        with self.assertRaises(ValidationError) as context:
            new_placement.full_clean()
        error_message = context.exception.message_dict.get('__all__', [])
        self.assertIn(
            "Constraint “Both bed fields must be equal to the total beds.” is violated.",
            error_message)

    def test_both_bed_fields_cannot_be_less_than_total_beds(self):
        """
        Test the both bed fields cannot be less than the total_beds fields.
        """

        new_placement = Placement(
            owner=self.user,
            category=self.category,
            title="Another Hotel by User",
            description="A" * 50,
            price=250,
            number_of_rooms=2,
            placement_area=43.5,
            total_beds=3,
            single_bed=1,
            double_bed=1,
        )

        with self.assertRaises(ValidationError) as context:
            new_placement.full_clean()
        error_message = context.exception.message_dict.get('__all__', [])
        self.assertIn(
            "Constraint “Both bed fields must be equal to the total beds.” is violated.",
            error_message)
