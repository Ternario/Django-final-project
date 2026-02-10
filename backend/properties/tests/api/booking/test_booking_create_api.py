from datetime import timedelta

from django.utils import timezone
from django.utils.timezone import now
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from properties.models import Booking

from properties.tests.api.booking.booking_setup import BookingSetup


class BookingCreateTest(BookingSetup):

    def setUp(self):
        super().setUp()

        self.now_date = timezone.now()
        self.number_date = f"BN{self.now_date.year}-{self.now_date.month:02d}{self.now_date.day:02d}"

    def test_landlord_can_create_new_booking(self):
        """
        Test if landlord user can create new Booking.
        Sends a Post request with properties data and expects a 201 CREATED response.
        Verifies that properties count increases and new properties has the correct link to landlord user and placement.
        """

        booking_data = {
            "placement": self.placement.id,
            "check_in_date": self.check_in_date3.strftime("%d-%m-%Y"),
            "check_out_date": self.check_out_date3.strftime("%d-%m-%Y"),
            "check_in_time": "11:00:00",
            "check_out_time": "10:00:00",
        }

        response = self.client.post(self.booking_create_url, booking_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], self.landlord_user.id)
        self.assertEqual(response.data["placement"], self.placement.id)
        self.assertEqual(response.data['booking_number'][:11], self.number_date)
        self.assertEqual(response.data["check_in_date"], self.check_in_date3.strftime("%d-%m-%Y"))
        self.assertEqual(response.data["check_out_date"], self.check_out_date3.strftime("%d-%m-%Y"))
        self.assertEqual(response.data["check_in_time"], "11:00")
        self.assertEqual(response.data["check_out_time"], "10:00")
        self.assertEqual(Booking.active_objects.count(), 4)

    def test_regular_user_can_create_new_booking(self):
        """
        Test if regular user can create new Booking.
        Sends a Post request with properties data and expects a 201 CREATED response.
        Verifies that properties count increases and new properties has the correct link to user and placement.
        """

        booking_data = {
            "placement": self.placement.id,
            "check_in_date": self.check_in_date3.strftime("%d-%m-%Y"),
            "check_out_date": self.check_out_date3.strftime("%d-%m-%Y"),
            "check_in_time": "11:00:00",
            "check_out_time": "10:00:00",
        }

        refresh = RefreshToken.for_user(self.regular_user)
        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.post(self.booking_create_url, booking_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"], self.regular_user.id)
        self.assertEqual(response.data["placement"], self.placement.id)
        self.assertEqual(response.data['booking_number'][:11], self.number_date)
        self.assertEqual(response.data["check_in_date"], self.check_in_date3.strftime("%d-%m-%Y"))
        self.assertEqual(response.data["check_out_date"], self.check_out_date3.strftime("%d-%m-%Y"))
        self.assertEqual(response.data["check_in_time"], "11:00")
        self.assertEqual(response.data["check_out_time"], "10:00")
        self.assertEqual(Booking.active_objects.count(), 4)

    def test_landlord_cannot_create_new_booking_to_his_own_apartment(self):
        """
        Test if landlord user cannot create new Booking to his own Apartment.
        Sends a Post request with properties data and expects a 400 BAD REQUEST response.
        Verifies that properties count has not increased.
        """

        booking_data = {
            "placement": self.placement2.id,
            "check_in_date": self.check_in_date3.strftime("%d-%m-%Y"),
            "check_out_date": self.check_out_date3.strftime("%d-%m-%Y"),
            "check_in_time": "11:00:00",
            "check_out_time": "10:00:00",
        }

        response = self.client.post(self.booking_create_url, booking_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["user"][0], "You can't properties your own apartment.")
        self.assertEqual(Booking.active_objects.count(), 3)

    def test_user_cannot_create_new_booking_with_empty_fields(self):
        """
        Test if user cannot create new Booking with empty placement, check_in_date or check_out_date field.
        Sends a Post request with empty properties fields and expects a 400 BAD REQUEST response.
        Verifies that properties count has not increased.
        """

        booking_data = {
            "placement": "",
            "check_in_date": None,
            "check_out_date": None,
            "check_in_time": None,
            "check_out_time": None,
        }

        response = self.client.post(self.booking_create_url, booking_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["placement"][0], "This field may not be null.")
        self.assertEqual(response.data["check_in_date"][0], "This field may not be null.")
        self.assertEqual(response.data["check_out_date"][0], "This field may not be null.")
        self.assertEqual(Booking.active_objects.count(), 3)

    def test_user_cannot_create_new_booking_with_past_check_in_date(self):
        """
        Test if user cannot create new Booking with check in date in the past.
        Sends a Post request with properties data and expects a 400 BAD REQUEST response.
        Verifies that properties count has not increased.
        """

        past_date = now().date() - timedelta(days=1)

        booking_data = {
            "placement": self.placement.id,
            "check_in_date": past_date.strftime("%d-%m-%Y"),
            "check_out_date": self.check_out_date3.strftime("%d-%m-%Y"),
            "check_in_time": "11:00:00",
            "check_out_time": "10:00:00",
        }

        response = self.client.post(self.booking_create_url, booking_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["check_in_date"][0], "Start date can't be in the past.")
        self.assertEqual(Booking.active_objects.count(), 3)

    def test_user_cannot_create_new_booking_with_date_less_than_one_day(self):
        """
        Test if user cannot create new Booking lasting less than one day.
        Sends a Post request with properties data and expects a 400 BAD REQUEST response.
        Verifies that properties count has not increased.
        """

        booking_data = {
            "placement": self.placement.id,
            "check_in_date": self.check_in_date3.strftime("%d-%m-%Y"),
            "check_out_date": self.check_in_date3.strftime("%d-%m-%Y"),
            "check_in_time": "11:00:00",
            "check_out_time": "10:00:00",
        }

        response = self.client.post(self.booking_create_url, booking_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["check_out_date"][0],
                         "The end date must be at least one day later than the start date.")
        self.assertEqual(Booking.active_objects.count(), 3)

    def test_user_cannot_create_new_booking_with_overlaps_dates(self):
        """
        Test if user cannot create new Booking with overlaps date.
        Sends a Post request with properties data and expects a 400 BAD REQUEST response.
        Verifies that properties count has not increased.
        """

        booking_data = {
            "placement": self.placement.id,
            "check_in_date": self.check_in_date1.strftime("%d-%m-%Y"),
            "check_out_date": self.check_out_date1.strftime("%d-%m-%Y"),
            "check_in_time": "11:00:00",
            "check_out_time": "10:00:00",
        }

        response = self.client.post(self.booking_create_url, booking_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0],
                         "This apartment is already reserved for the selected dates.")
        self.assertEqual(Booking.active_objects.count(), 3)

    def test_unauthenticated_user_cannot_create_new_booking(self):
        """
        Test if unauthenticated user cannot create new Booking.
        Sends a Post request with properties data and expects a 401 UNAUTHORIZED response.
        Verifies that properties count has not increased.
        """

        booking_data = {
            "placement": self.placement.id,
            "check_in_date": self.check_in_date3.strftime("%d-%m-%Y"),
            "check_out_date": self.check_out_date3.strftime("%d-%m-%Y"),
            "check_in_time": "11:00:00",
            "check_out_time": "10:00:00",
        }

        self.client.cookies.clear()

        response = self.client.post(self.booking_create_url, booking_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")
        self.assertEqual(Booking.active_objects.count(), 3)
