import datetime

from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from booking.models import Placement, PlacementLocation
from booking.tests.api.placement.placement_setup import PlacementSetup


class PlacementSearchTest(PlacementSetup):

    def setUp(self):
        super().setUp()

        self.placement2 = Placement.objects.create(
            owner=self.landlord_user,
            category=self.hostel_category,
            title="Second Hostel by Landlord User",
            description="A" * 50 + "hostel one",
            price=150,
            number_of_rooms=3,
            placement_area=43.5,
            total_beds=3,
            single_bed=2,
            double_bed=1,
            is_active=True
        )

        self.placement_location2 = PlacementLocation.objects.create(
            placement=self.placement2,
            country="Test Country",
            city="Test second city",
            post_code="12045",
            street="Test street",
            house_number="1"
        )

        self.placement3 = Placement.objects.create(
            owner=self.landlord_user,
            category=self.hotel_category,
            title="Third Hotel by Landlord User",
            description="A" * 50 + "hotel one",
            price=550,
            number_of_rooms=2,
            placement_area=43.5,
            total_beds=3,
            single_bed=2,
            double_bed=1,
            is_active=True
        )

        self.placement_location3 = PlacementLocation.objects.create(
            placement=self.placement3,
            country="Test Country",
            city="Test third city",
            post_code="56405",
            street="Test street",
            house_number="1"
        )

        Placement.objects.filter(id=self.placement.id).update(
            created_at=timezone.now() - datetime.timedelta(days=6)
        )

        Placement.objects.filter(id=self.placement2.id).update(
            created_at=timezone.now() - datetime.timedelta(days=4)
        )
        Placement.objects.filter(id=self.placement3.id).update(
            created_at=timezone.now() - datetime.timedelta(days=1)
        )

        self.placement.refresh_from_db()
        self.placement2.refresh_from_db()
        self.placement3.refresh_from_db()

    def test_user_retrieve_active_placements_list(self):
        """
        Test if user can retrieve the list of active Placements and ordering by created_at is desc.
        Sends a Get request and expects a 200 OK response.
        Verifies that the number of retrieved placement and all active Placements are the same and the order is correct.
        """

        response = self.client.get(self.placement_active_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Placement.objects.all().count())
        self.assertEqual(response.data[0]["created_at"], self.placement3.created_at.strftime("%d-%m-%Y"))
        self.assertEqual(response.data[-1]["created_at"], self.placement.created_at.strftime("%d-%m-%Y"))

    def test_user_retrieve_active_placements_list_by_creation_date_asc(self):
        """
        Test if user can retrieve the list of active Placements according to the created_at query parameters.
        Sends a Get request and expects a 200 OK response.
        Verifies that the number of retrieved placement and all active Placements are the same and the order is correct.
        """

        response = self.client.get(self.placement_active_list_url, data={"ordering": "created_at"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Placement.objects.all().count())
        self.assertEqual(response.data[0]["created_at"], self.placement.created_at.strftime("%d-%m-%Y"))
        self.assertEqual(response.data[-1]["created_at"], self.placement3.created_at.strftime("%d-%m-%Y"))

    def test_user_retrieve_active_placements_list_by_text(self):
        """
        Test if user can retrieve the list of active Placements according to the text query parameters.
        Sends a Get request and expects a 200 OK response.
        Verifies that the number and data of retrieved placement is correct.
        """

        response = self.client.get(self.placement_active_list_url, data={"text": "Hotel"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Placement.objects.filter(
            Q(title__icontains="Hotel") | Q(description__icontains="Hotel")).count())

    def test_user_retrieve_active_placements_list_by_price_desc(self):
        """
        Test if user can retrieve the list of active Placements according to the price descending query parameters.
        Sends a Get request and expects a 200 OK response.
        Verifies that the number and data of retrieved placement is correct.
        """

        response = self.client.get(self.placement_active_list_url, data={"ordering": "-price"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data[0]["price"]), float(self.placement3.price))
        self.assertEqual(float(response.data[-1]["price"]), float(self.placement2.price))

    def test_user_retrieve_active_placements_list_by_price_asc(self):
        """
        Test if user can retrieve the list of active Placements according to the price ascending query parameters.
        Sends a Get request and expects a 200 OK response.
        Verifies that the number and data of retrieved placement is correct.
        """

        response = self.client.get(self.placement_active_list_url, data={"ordering": "price"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data[0]["price"]), float(self.placement2.price))
        self.assertEqual(float(response.data[-1]["price"]), float(self.placement3.price))

    def test_user_retrieve_placements_list_by_city(self):
        """
        Test if user can retrieve the list of active Placements according to the city query parameters.
        Sends a Get request and expects a 200 OK response.
        Verifies that the number and data of retrieved placement is correct.
        """
        response = self.client.get(self.placement_active_list_url, data={"city": "Test first city,Test second city"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),
                         Placement.objects.filter(
                             placement_location__city__in=["Test first city", "Test second city"]).count())

    def test_user_retrieve_placements_list_by_category(self):
        """
        Test if user can retrieve the list of active Placements according to the category query parameters.
        Sends a Get request and expects a 200 OK response.
        Verifies that the number and data of retrieved placement is correct.
        """
        response = self.client.get(self.placement_active_list_url, data={"category": "Hotels"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),
                         Placement.objects.filter(category__name__in=["Hotels"]).count())

    def test_user_retrieve_placements_list_by_details(self):
        """
        Test if user can retrieve the list of active Placements according to the details query parameters.
        Sends a Get request and expects a 200 OK response.
        Verifies that the number and data of retrieved placement is correct.
        """
        response = self.client.get(self.placement_active_list_url,
                                   data={"details": "pets,room_service,balcony,coffee_tee_maker"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),
                         Placement.objects.filter(placement_details__pets=True, placement_details__room_service=True,
                                                  placement_details__balcony=True,
                                                  placement_details__coffee_tee_maker=True).count())

    def test_user_retrieve_placements_list_by_rooms_number(self):
        """
        Test if user can retrieve the list of active Placements according to the rooms number query parameters.
        Sends a Get request and expects a 200 OK response.
        Verifies that the number and data of retrieved placement is correct.
        """
        response = self.client.get(self.placement_active_list_url, data={"no_rooms": "2"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),
                         Placement.objects.filter(number_of_rooms__in=[2]).count())

    def test_user_retrieve_placements_list_by_price_range(self):
        """
        Test if user can retrieve the list of active Placements according to the price range query parameters.
        Sends a Get request and expects a 200 OK response.
        Verifies that the number and data of retrieved placement is correct.
        """
        response = self.client.get(self.placement_active_list_url, data={"price_gte": "200", "price_lte": "400"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),
                         Placement.objects.filter(price__gte=200, price__lte=400).count())

    def test_user_retrieve_placements_list_by_multy_params(self):
        """
        Test if user can retrieve the list of active Placements according to the multiple query parameters.
        Sends a Get request and expects a 200 OK response.
        Verifies that the number and data of retrieved placement is correct.
        """

        data = {
            "city": "Test first city",
            "price_gte": "200",
            "price_lte": "400",
            "no_rooms": "2",
            "details": "pets,room_service,balcony,coffee_tee_maker"
        }

        response = self.client.get(self.placement_active_list_url, data=data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),
                         Placement.objects.filter(placement_location__city__in=["Test first city"], price__gte=200,
                                                  price__lte=400, number_of_rooms__in=[2], placement_details__pets=True,
                                                  placement_details__room_service=True,
                                                  placement_details__balcony=True,
                                                  placement_details__coffee_tee_maker=True).count())

    def test_user_owner_can_retrieve_his_active_placements_list(self):
        """
        Test if owner user can retrieve his list of active Placements.
        Sends a GET request and expects a 200 OK response.
        Verifies that the user receive the correct linked placement data.
        """

        response = self.client.get(self.my_active_placement_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_regular_user_cannot_retrieve_active_placements_list(self):
        """
        Test if regular user cannot retrieve the list of inactive Placements.
        Sends a GET request and expects a 403 FORBIDDEN response.
        Verifies that the user receive the correct answer.
        """

        refresh = RefreshToken.for_user(self.regular_user)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.get(self.my_active_placement_list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You do not have permission to perform this action.")

    def test_user_owner_can_retrieve_his_inactive_placements_list(self):
        """
        Test if owner user can retrieve his list of inactive Placements.
        Sends a GET request and expects a 200 OK response.
        Verifies that the user receive the correct Placements data.
        """

        response = self.client.get(self.my_inactive_placement_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_regular_user_cannot_retrieve_inactive_placements_list(self):
        """
        Test if regular user cannot retrieve the list of inactive Placements.
        Sends a GET request and expects a 403 FORBIDDEN response.
        Verifies that the user receive the correct answer.
        """

        refresh = RefreshToken.for_user(self.regular_user)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.get(self.my_inactive_placement_list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "You do not have permission to perform this action.")
