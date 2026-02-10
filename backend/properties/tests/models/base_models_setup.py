from django.test import TestCase

from properties.models import Placement, User, Category


class BaseModelSetupTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.landlord_user = User.objects.create(
            email="landlorduser@example.com",
            first_name="User",
            last_name="User",
            username="LandlordUser",
            phone="+1204506589",
            is_landlord=True
        )

        cls.category = Category.objects.create(
            name="Hotels"
        )

        cls.placement = Placement.objects.create(
            owner=cls.landlord_user,
            category=cls.category,
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
