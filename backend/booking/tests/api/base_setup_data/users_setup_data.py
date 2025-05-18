from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from booking.models import User, Category


class BaseUsersSetupData(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.landlord_user = User.objects.create(
            email="landlorduser@example.com",
            first_name="User",
            last_name="User",
            username="FirstLandlordUser",
            phone="+1234567899",
            password="userpassword",
            is_landlord=True
        )

        cls.landlord_user2 = User.objects.create(
            email="secondlandlorduser@example.com",
            first_name="User",
            last_name="User",
            username="SecondLandlordUser",
            phone="+123907899",
            password="userpassword",
            is_landlord=True
        )

        cls.regular_user = User.objects.create(
            email="user@example.com",
            first_name="User",
            last_name="User",
            username="FirstRegularUser",
            phone="+1234568999",
            password="userpassword",
            is_landlord=False
        )

        cls.hotel_category = Category.objects.create(name="Hotels")
        cls.hostel_category = Category.objects.create(name="Hostels")

    def setUp(self):
        self.client = APIClient()

        refresh = RefreshToken.for_user(self.landlord_user)
        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)
