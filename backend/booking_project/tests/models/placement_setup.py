from django.test import TestCase

from booking_project.models import Placement, User, Category


class PlacementSetupTest(TestCase):

    def setUp(self):
        self.landlord_user = User.objects.create(
            email="landlorduser@example.com",
            first_name="User",
            last_name="User",
            username="LandlordUser",
            phone="+1204506589",
            is_landlord=True
        )

        self.category = Category.objects.create(
            name="Hotels"
        )

        self.placement = Placement.objects.create(
            owner=self.landlord_user,
            category=self.category,
            title="Hotel by User",
            description="A" * 50,
            price=250,
            number_of_rooms=2,
            placement_area=43.5,
            total_beds=3,
            single_bed=2,
            double_bed=1,
            is_active=True
        )
