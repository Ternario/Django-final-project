from django.core.exceptions import ValidationError

from booking.models import PlacementDetails
from booking.tests.models.placement_setup import PlacementSetupTest


class PlacementDetailsModelTest(PlacementSetupTest):

    def setUp(self):
        super().setUp()

        self.placement_details = PlacementDetails.objects.create(
            placement=self.placement,
            pets=True,
            free_wifi=False,
            smoking=False,
            parking=False,
            room_service=True,
            front_desk_allowed_24=False,
            free_cancellation=False,
            balcony=True,
            air_conditioning=False,
            washing_machine=False,
            kitchenette=False,
            tv=False,
            coffee_tee_maker=True
        )

    def test_create_placement_details(self):
        """Test creating a placement details."""

        self.assertIsNotNone(self.placement_details.id)
        self.assertIsNotNone(self.placement_details.placement)
        self.assertEqual(self.placement_details.placement, self.placement)
        self.assertTrue(self.placement_details.pets)
        self.assertFalse(self.placement_details.parking)
        self.assertTrue(self.placement_details.room_service)
        self.assertFalse(self.placement_details.washing_machine)
        self.assertTrue(self.placement_details.balcony)
        self.assertTrue(self.placement_details.coffee_tee_maker)

    def test_one_placement_has_one_details(self):
        """Test the one placement cannot have second (or more) details model"""

        new_details = PlacementDetails(
            placement=self.placement,
        )

        with self.assertRaises(ValidationError) as context:
            new_details.full_clean()
        error_message = context.exception.message_dict.get("placement", [])
        self.assertIn("Placement Detail with this Placement already exists.", error_message)

    def test_placement_details_cannot_be_created_without_placement(self):
        """Test the placement details cannot be created without placement field."""

        new_details = PlacementDetails(
            placement=None,
        )

        with self.assertRaises(ValidationError) as context:
            new_details.full_clean()
        error_message = context.exception.message_dict.get("placement", [])
        self.assertIn("This field cannot be null.", error_message)
