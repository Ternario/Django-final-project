from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from booking.models import Placement, PlacementImage
from booking.tests.api.placement.placement_setup import PlacementSetup


class PlacementActivationTest(PlacementSetup):
    def test_user_owner_can_deactivate_placement(self):
        """
        Test if owner user can deactivate Placement.
        Sends a PATCH request with data and expects 200 OK response.
        Verifies that the Placement has been updated correctly.
        """

        response = self.client.patch(self.placement_activation(self.placement.pk), {"activate": False}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Placement.objects.count(), 0)
        self.assertFalse(Placement.all_objects.get(pk=self.placement.pk).is_active)

    def test_user_owner_can_activate_placement(self):
        """
        Test if owner user can activate Placement.
        Sends a PATCH request with data and expects 200 OK response.
        Verifies that the Placement has been updated correctly.
        """

        response = self.client.patch(self.placement_activation(self.inactive_placement.pk), {"activate": True},
                                     format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Placement.objects.count(), 2)
        self.assertTrue(Placement.objects.get(pk=self.inactive_placement.pk).is_active)

    def test_user_owner_cannot_activate_placement_without_images(self):
        """
        Test if owner user cannot activate Placement without images.
        Sends a PATCH request with data and expects 400 BAD REQUEST response.
        Verifies that the Placement hasn't been activated.
        """

        PlacementImage.objects.filter(placement=self.inactive_placement.pk).delete()

        response = self.client.patch(self.placement_activation(self.inactive_placement.pk), {"activate": True},
                                     format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["activate"][0], "You need to fill in the placement details or add photos.")
        self.assertEqual(Placement.objects.count(), 1)
        self.assertFalse(Placement.all_objects.get(pk=self.inactive_placement.pk).is_active)

    def test_user_owner_cannot_activate_placement_without_details(self):
        """
        Test if owner user cannot activate Placement without details.
        Sends the first PUT request with all False details and expects 200 OK response
        """

        details_data = {
            "pets": False,
            "free_wifi": False,
            "smoking": False,
            "parking": False,
            "room_service": False,
            "front_desk_allowed_24": False,
            "free_cancellation": False,
            "balcony": False,
            "air_conditioning": False,
            "washing_machine": False,
            "kitchenette": False,
            "tv": False,
            "coffee_tee_maker": False,
        }

        first_response = self.client.put(self.placement_details_retrieve_update_url(self.inactive_placement.pk),
                                         details_data, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        """
        Sends the second PATCH request with data and expects 400 BAD REQUEST response.
        Verifies that the Placement hasn't been activated.
        """

        second_response = self.client.patch(self.placement_activation(self.inactive_placement.pk), {"activate": True},
                                            format="json")

        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(second_response.data["activate"][0],
                         "You need to fill in the placement details or add photos.")
        self.assertEqual(Placement.objects.count(), 1)
        self.assertFalse(Placement.all_objects.get(pk=self.inactive_placement.pk).is_active)

    def test_unauthorized_user_owner_cannot_deactivate_placement(self):
        """
        Test if unauthorized owner user cannot deactivate Placement.
        Sends a PATCH request with data and expects 401 UNAUTHORIZED response.
        Verifies that the Placement hasn't been deactivated.
        """

        self.client.cookies.clear()

        response = self.client.patch(self.placement_activation(self.placement.pk), {"activate": False}, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")
        self.assertEqual(Placement.objects.count(), 1)
        self.assertTrue(Placement.all_objects.get(pk=self.placement.pk).is_active)

    def test_another_landlord_user_cannot_deactivate_placement(self):
        """
        Test if another Landlord user cannot deactivate Placement.
        Sends a PATCH request with data and expects 403 FORBIDDEN response.
        Verifies that the Placement hasn't been deactivated.
        """

        refresh = RefreshToken.for_user(self.landlord_user2)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.patch(self.placement_activation(self.placement.pk), {"activate": False}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertEqual(Placement.objects.count(), 1)
        self.assertTrue(Placement.all_objects.get(pk=self.placement.pk).is_active)

    def test_regular_user_cannot_deactivate_placement(self):
        """
        Test if regular user cannot deactivate Placement.
        Sends a PATCH request with data and expects 403 FORBIDDEN response.
        Verifies that the Placement hasn't been deactivated.
        """

        refresh = RefreshToken.for_user(self.regular_user)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.patch(self.placement_activation(self.placement.pk), {"activate": False}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertEqual(Placement.objects.count(), 1)
        self.assertTrue(Placement.all_objects.get(pk=self.placement.pk).is_active)
