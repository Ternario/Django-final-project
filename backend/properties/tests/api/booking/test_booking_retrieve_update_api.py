from django.utils.timezone import now
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from properties.models import Placement, Booking
from properties.utils.choices.booking import BookingStatus

from properties.tests.api.booking.booking_setup import BookingSetup


class BookingRetrieveUpdateTest(BookingSetup):
    def test_landlord_user_can_retrieve_booking_that_was_reserved_by_other_booking(self):
        """
        Test if landlord user can get info about the properties that other users have reserved.
        Sends a GET request and expects 200 Ok response.
        Verifies that the user receive the correct data.
        """

        refresh = RefreshToken.for_user(self.landlord_user2)
        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.get(self.booking_placement_owner_retrieve_update(self.booking.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.booking.pk)
        self.assertEqual(response.data["user"]["id"], self.landlord_user.pk)
        self.assertEqual(response.data["placement"], self.placement.id)
        self.assertEqual(Placement.objects.get(pk=response.data["placement"]).owner, self.landlord_user2)

    def test_landlord_user_can_retrieve_booking_that_he_reserved(self):
        """
        Test if landlord user can get info about the properties that he has reserved.
        Sends a GET request and expects 200 Ok response.
        Verifies that the user receive the correct data.
        """

        response = self.client.get(self.booking_owner_retrieve_update(self.booking.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.booking.pk)
        self.assertEqual(response.data["placement"], self.placement.pk)
        self.assertEqual(response.data["user"], self.landlord_user.pk)
        self.assertEqual(Placement.objects.get(pk=response.data["placement"]).owner, self.landlord_user2)

    def test_landlord_placement_owner_can_cancel_booking(self):
        """
        Test if landlord placement owner can cancel the properties.
        Sends a PUT request and expects 200 Ok response.
        Verifies that the properties has been cancelled and user receive the correct data.
        """

        refresh = RefreshToken.for_user(self.landlord_user2)
        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        booking_data = {
            "cancellation_reason": "A" * 60
        }

        response = self.client.put(self.booking_placement_owner_retrieve_update(self.booking.pk), booking_data,
                                   format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status_display"], BookingStatus.CANCELLED.value)
        self.assertEqual(response.data["cancellation_reason"], "A" * 60)
        self.assertEqual(response.data["cancelled_at"], now().strftime("%d-%m-%Y %H:%M"))
        self.assertEqual(response.data["cancelled_by_role"], "Owner")
        self.assertEqual(response.data["cancelled_by"], self.landlord_user2.pk)
        self.assertTrue(Booking.inactive_objects.get(pk=self.booking.pk))
        self.assertEqual(Booking.inactive_objects.count(), 3)

    def test_user_can_cancel_booking(self):
        """
        Test if user can cancel the properties.
        Sends a PUT request and expects 200 Ok response.
        Verifies that the properties has been cancelled and user receive the correct data.
        """

        booking_data = {
            "cancellation_reason": "A" * 60
        }

        response = self.client.put(self.booking_owner_retrieve_update(self.booking.pk), booking_data,
                                   format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status_display"], BookingStatus.CANCELLED.value)
        self.assertEqual(response.data["cancellation_reason"], "A" * 60)
        self.assertEqual(response.data["cancelled_at"], now().strftime("%d-%m-%Y %H:%M"))
        self.assertEqual(response.data["cancelled_by_role"], "User")
        self.assertEqual(response.data["cancelled_by"], self.landlord_user.pk)
        self.assertTrue(Booking.inactive_objects.get(pk=self.booking.pk))
        self.assertEqual(Booking.inactive_objects.count(), 3)

    def test_unauthenticated_user_cannot_retrieve_booking(self):
        """
        Test if unauthenticated user cannot get info about the properties.
        Sends a GET request and expects 401 UNAUTHORIZED response.
        Verifies that the user receive the correct data.
        """

        self.client.cookies.clear()

        response = self.client.get(self.booking_owner_retrieve_update(self.booking.pk))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")

    def test_landlord_placement_owner_cannot_cancel_booking_less_than_two_days(self):
        """
        Test if landlord placement owner cannot cancel the properties less than two days in advance.
        Sends a PUT request and expects 400 BAD REQUEST response.
        Verifies that the properties has not been cancelled and user receive the correct data.
        """

        refresh = RefreshToken.for_user(self.landlord_user)
        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        booking_data = {
            "cancellation_reason": "A" * 60
        }

        response = self.client.put(self.booking_placement_owner_retrieve_update(self.booking2.pk), booking_data,
                                   format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0],
                         "You cannot cancel the properties less than two days in advance.")
        self.assertTrue(Booking.active_objects.get(pk=self.booking2.pk))
        self.assertEqual(Booking.active_objects.count(), 3)

    def test_user_cannot_cancel_booking_less_then_two_days(self):
        """
        Test if user cannot cancel the properties less than two days in advance.
        Sends a PUT request and expects 400 BAD REQUEST response.
        Verifies that the properties has not been cancelled and user receive the correct data.
        """

        refresh = RefreshToken.for_user(self.regular_user)
        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        booking_data = {
            "cancellation_reason": "A" * 60
        }

        response = self.client.put(self.booking_owner_retrieve_update(self.booking2.pk), booking_data,
                                   format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0],
                         "You cannot cancel the properties less than two days in advance.")
        self.assertTrue(Booking.active_objects.get(pk=self.booking2.pk))
        self.assertEqual(Booking.active_objects.count(), 3)

    def test_unauthenticated_user_cannot_cancel_booking(self):
        """
        Test if unauthenticated user cannot cancel the properties.
        Sends a PUT request and expects 401 UNAUTHORIZED response.
        Verifies that the properties has not been cancelled and user receive the correct data.
        """

        booking_data = {
            "cancellation_reason": "A" * 60
        }

        self.client.cookies.clear()

        response = self.client.put(self.booking_owner_retrieve_update(self.booking.pk), booking_data,
                                   format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")
        self.assertTrue(Booking.active_objects.get(pk=self.booking.pk))
        self.assertEqual(Booking.active_objects.count(), 3)

    def test_landlord_placement_owner_cannot_delete_booking(self):
        """
        Test if landlord placement owner cannot delete the properties.
        Sends a DELETE request and expects 405 METHOD NOT ALLOWED response.
        Verifies that the properties has not been deleted and user receive the correct data.
        """

        refresh = RefreshToken.for_user(self.landlord_user2)
        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.delete(self.booking_placement_owner_retrieve_update(self.booking.pk))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data["detail"], "Method \"DELETE\" not allowed.")
        self.assertEqual(Booking.objects.count(), 5)

    def test_user_cannot_delete_booking(self):
        """
        Test if user cannot delete the properties.
        Sends a DELETE request and expects 405 METHOD NOT ALLOWED response.
        Verifies that the properties has not been deleted and user receive the correct data.
        """

        response = self.client.delete(self.booking_owner_retrieve_update(self.booking.pk))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data["detail"], "Method \"DELETE\" not allowed.")
        self.assertEqual(Booking.objects.count(), 5)
