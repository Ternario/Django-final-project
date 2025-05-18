from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from booking.models import PlacementDetails
from booking.tests.api.placement.placement_setup import PlacementSetup


class PlacementDetailsRetrieveUpdateTest(PlacementSetup):
    def test_user_owner_can_retrieve_details(self):
        """
        Test if owner user can retrieve Placement Details.
        Sends a GET request and expects 200 OK response.
        Verifies that the Placement Details has correct link to Placement.
        """

        response = self.client.get(self.placement_details_retrieve_update_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["placement"], self.placement.pk)

    def test_user_owner_can_retrieve_details_inactive_placement(self):
        """
        Test if owner user can retrieve Placement Details inactive Placement.
        Sends a GET request and expects 200 OK response.
        Verifies that the Placement Details has correct link to Placement.
        """

        response = self.client.get(self.placement_details_retrieve_update_url(self.inactive_placement.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["placement"], self.inactive_placement.pk)

    def test_user_owner_can_update_details(self):
        """
        Test if owner user can update Placement Details.
        Sends a PUT request with new data and expects 200 OK response.
        Verifies that the Placement Details has been updated correctly.
        """

        details_data = {
            "pets": False,
            "free_wifi": False,
            "smoking": False,
            "parking": True,
            "room_service": True,
            "front_desk_allowed_24": False,
            "free_cancellation": False,
            "balcony": False,
            "air_conditioning": False,
            "washing_machine": True,
            "kitchenette": False,
            "tv": False,
            "coffee_tee_maker": True
        }

        response = self.client.put(self.placement_details_retrieve_update_url(self.placement.pk), details_data,
                                   fromat="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["smoking"])
        self.assertFalse(response.data["front_desk_allowed_24"])
        self.assertFalse(response.data["air_conditioning"])
        self.assertTrue(response.data["parking"])
        self.assertTrue(response.data["room_service"])
        self.assertTrue(response.data["washing_machine"])
        self.assertTrue(response.data["coffee_tee_maker"])

    def test_user_owner_can_update_details_inactive_placement(self):
        """
        Test if owner user can update Placement Details inactive Placement.
        Sends a PUT request with new data and expects 200 OK response.
        Verifies that the Placement Details has been updated correctly.
        """

        details_data = {
            "pets": False,
            "free_wifi": False,
            "smoking": False,
            "parking": True,
            "room_service": True,
            "front_desk_allowed_24": False,
            "free_cancellation": False,
            "balcony": False,
            "air_conditioning": False,
            "washing_machine": True,
            "kitchenette": False,
            "tv": False,
            "coffee_tee_maker": True
        }

        response = self.client.put(self.placement_details_retrieve_update_url(self.inactive_placement.pk), details_data,
                                   fromat="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["smoking"])
        self.assertFalse(response.data["front_desk_allowed_24"])
        self.assertFalse(response.data["air_conditioning"])
        self.assertTrue(response.data["parking"])
        self.assertTrue(response.data["room_service"])
        self.assertTrue(response.data["washing_machine"])
        self.assertTrue(response.data["coffee_tee_maker"])

    def test_user_owner_cannot_delete_details(self):
        """
        Test if owner user cannot delete Placement Details.
        Sends a DELETE request a and expects 405 METHOD NOT ALLOWED response.
        Verifies that the Placement Details hasn't been deleted.
        """

        response = self.client.delete(self.placement_details_retrieve_update_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data["detail"], "Method \"DELETE\" not allowed.")
        self.assertTrue(PlacementDetails.objects.get(placement=self.placement.pk))

    def test_unauthorized_user_owner_cannot_retrieve_details(self):
        """
        Test if unauthorized owner user cannot retrieve Placement Details.
        Sends a GET request and expects 401 UNAUTHORIZED response.
        Verifies that the user receive the correct answer.
        """

        self.client.cookies.clear()

        response = self.client.get(self.placement_details_retrieve_update_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")

    def test_unauthorized_user_owner_cannot_update_details(self):
        """
        Test if unauthorized owner user cannot update Placement Details.
        Sends a PUT request with new data and expects 401 UNAUTHORIZED response.
        Verifies that the Placement Details hasn't been updated.
        """

        details_data = {
            "pets": False,
            "free_wifi": False,
            "smoking": True,
            "parking": True,
            "room_service": False,
            "front_desk_allowed_24": True,
            "free_cancellation": False,
            "balcony": False,
            "air_conditioning": False,
            "washing_machine": True,
            "kitchenette": False,
            "tv": False,
            "coffee_tee_maker": True
        }

        self.client.cookies.clear()

        response = self.client.put(self.placement_details_retrieve_update_url(self.placement.pk), details_data,
                                   fromat="json")

        placement_details = PlacementDetails.objects.get(placement=self.placement.pk)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")
        self.assertFalse(placement_details.smoking)
        self.assertFalse(placement_details.parking)
        self.assertFalse(placement_details.front_desk_allowed_24)
        self.assertTrue(placement_details.pets)
        self.assertTrue(placement_details.room_service)
        self.assertTrue(placement_details.balcony)
        self.assertTrue(placement_details.coffee_tee_maker)

    def test_another_landlord_user_cannot_retrieve_details(self):
        """
        Test if another Landlord user cannot retrieve Placement Details.
        Sends a GET request and expects 403 FORBIDDEN response.
        Verifies that the user receive the correct answer.
        """

        refresh = RefreshToken.for_user(self.landlord_user2)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.get(self.placement_details_retrieve_update_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")

    def test_another_landlord_user_cannot_update_details(self):
        """
        Test if another Landlord user cannot update Placement Details.
        Sends a PUT request with new data and expects 403 FORBIDDEN response.
        Verifies that the Placement Details hasn't been updated.
        """

        details_data = {
            "pets": False,
            "free_wifi": False,
            "smoking": True,
            "parking": True,
            "room_service": False,
            "front_desk_allowed_24": True,
            "free_cancellation": False,
            "balcony": False,
            "air_conditioning": False,
            "washing_machine": True,
            "kitchenette": False,
            "tv": False,
            "coffee_tee_maker": True
        }

        refresh = RefreshToken.for_user(self.landlord_user2)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.put(self.placement_details_retrieve_update_url(self.placement.pk), details_data,
                                   fromat="json")

        placement_details = PlacementDetails.objects.get(placement=self.placement.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertFalse(placement_details.smoking)
        self.assertFalse(placement_details.parking)
        self.assertFalse(placement_details.front_desk_allowed_24)
        self.assertTrue(placement_details.pets)
        self.assertTrue(placement_details.room_service)
        self.assertTrue(placement_details.balcony)
        self.assertTrue(placement_details.coffee_tee_maker)

    def test_regular_user_cannot_retrieve_details(self):
        """
        Test if regular user cannot retrieve Placement Details.
        Sends a GET request and expects 403 FORBIDDEN response.
        Verifies that the user receive the correct answer.
        """

        refresh = RefreshToken.for_user(self.regular_user)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.get(self.placement_details_retrieve_update_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")

    def test_regular_user_cannot_update_details(self):
        """
        Test if regular user cannot update Placement Details.
        Sends a PUT request with new data and expects 403 FORBIDDEN response.
        Verifies that the Placement Details hasn't been updated.
        """

        details_data = {
            "pets": False,
            "free_wifi": False,
            "smoking": True,
            "parking": True,
            "room_service": False,
            "front_desk_allowed_24": True,
            "free_cancellation": False,
            "balcony": False,
            "air_conditioning": False,
            "washing_machine": True,
            "kitchenette": False,
            "tv": False,
            "coffee_tee_maker": True
        }

        refresh = RefreshToken.for_user(self.regular_user)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.put(self.placement_details_retrieve_update_url(self.placement.pk), details_data,
                                   fromat="json")

        placement_details = PlacementDetails.objects.get(placement=self.placement.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertFalse(placement_details.smoking)
        self.assertFalse(placement_details.parking)
        self.assertFalse(placement_details.front_desk_allowed_24)
        self.assertTrue(placement_details.pets)
        self.assertTrue(placement_details.room_service)
        self.assertTrue(placement_details.balcony)
        self.assertTrue(placement_details.coffee_tee_maker)
