from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from properties.models import Booking
from properties.utils.choices.time import CheckInTime, CheckOutTime

from properties.tests.api.booking.booking_setup import BookingSetup


class BookingFilterTest(BookingSetup):
    def test_user_can_retrieve_time_choices_list(self):
        """
        Test if user can retrieve list of times choices.
        Sends a GET request and expects 200 OK response.
        Verifies that the user receive correct data.
        """

        response = self.client.get(self.booking_choices_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["check_in_time"]), len(CheckInTime.choices()))
        self.assertEqual(len(response.data["check_out_time"]), len(CheckOutTime.choices()))

    def test_landlord_user_can_retrieve_booking_list_his_placements(self):
        """
        Test if landlord user can retrieve list of bookings of his placements.
        Sends a GET request and expects 200 OK response.
        Verifies that the user receive correct data.
        """

        refresh = RefreshToken.for_user(self.landlord_user2)
        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.get(self.booking_placement_owner_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Booking.active_objects.filter(placement__owner=self.landlord_user2).count())

    def test_user_can_retrieve_list_his_bookings(self):
        """
        Test if user can retrieve list of his bookings.
        Sends a GET request and expects 200 OK response.
        Verifies that the user receive correct data.
        """

        response = self.client.get(self.booking_owner_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Booking.active_objects.filter(user=self.landlord_user).count())

    def test_landlord_user_can_retrieve_inactive_bookings_list_his_placements(self):
        """
        Test if landlord user can retrieve list of inactive bookings of his placements.
        Sends a GET request and expects 200 OK response.
        Verifies that the user receive correct data.
        """

        refresh = RefreshToken.for_user(self.landlord_user2)
        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.get(self.inactive_booking_placement_owner_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),
                         Booking.inactive_objects.filter(placement__owner=self.landlord_user2).count())

    def test_user_can_retrieve_inactive_list_his_bookings(self):
        """
        Test if user can retrieve list of his inactive bookings.
        Sends a GET request and expects 200 OK response.
        Verifies that the user receive correct data.
        """

        response = self.client.get(self.inactive_booking_owner_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Booking.inactive_objects.filter(user=self.landlord_user).count())

    def test_user_can_retrieve_list_his_bookings_by_query_params(self):
        """
        Test if user can retrieve list of his bookings by query parameters.
        Sends a GET request and expects 200 OK response.
        Verifies that the user receive correct data.
        """

        response = self.client.get(self.booking_owner_list_url, data={"status": "Confirmed"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),
                         Booking.active_objects.filter(user=self.landlord_user, status="Confirmed").count())

    def test_user_can_retrieve_inactive_list_his_bookings_by_query_params(self):
        """
        Test if user can retrieve list of his inactive bookings by query parameters.
        Sends a GET request and expects 200 OK response.
        Verifies that the user receive correct data.
        """

        response = self.client.get(self.inactive_booking_owner_list, data={"status": "Completed"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data),
                         Booking.inactive_objects.filter(user=self.landlord_user, status="Completed").count())

    def test_unauthenticated_user_cannot_retrieve_bookings_list(self):
        """
        Test if unauthenticated user cannot get info about the list of bookings.
        Sends a GET request and expects 401 UNAUTHORIZED response.
        Verifies that the user receive the correct data.
        """

        self.client.cookies.clear()

        response = self.client.get(self.booking_owner_list_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")
