from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from properties.models import PlacementLocation
from properties.tests.api.placement.placement_setup import PlacementSetup


class PlacementLocationRetrieveUpdateTest(PlacementSetup):

    def test_user_owner_can_retrieve_location(self):
        """
        Test if owner user can retrieve Placement Location.
        Sends a GET request and expects 200 OK response.
        Verifies that the Placement Location has correct link to Placement.
        """

        response = self.client.get(self.placement_location_retrieve_update_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["placement"], self.placement.pk)

    def test_user_owner_can_retrieve_location_inactive_placement(self):
        """
        Test if owner user can retrieve Placement Location inactive Placement.
        Sends a GET request and expects 200 OK response.
        Verifies that the Placement Location has correct link to Placement.
        """

        response = self.client.get(self.placement_location_retrieve_update_url(self.inactive_placement.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["placement"], self.inactive_placement.pk)

    def test_user_owner_can_update_location(self):
        """
        Test if owner user can update Placement Location.
        Sends a PUT request with new data and expects 200 OK response.
        Verifies that the Placement Location has been updated correctly.
        """

        location_data = {
            "country": "Test Country",
            "city": "Updated first city",
            "post_code": "18505",
            "street": "Updated street",
            "house_number": "3/4"
        }

        response = self.client.put(self.placement_location_retrieve_update_url(self.placement.pk), location_data,
                                   fromat="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["city"], "Updated first city")
        self.assertEqual(response.data["post_code"], "18505")
        self.assertEqual(response.data["street"], "Updated street")
        self.assertEqual(response.data["house_number"], "3/4")

    def test_user_owner_can_update_location_inactive_placement(self):
        """
        Test if owner user can update Placement Location inactive Placement.
        Sends a PUT request with new data and expects 200 OK response.
        Verifies that the Placement Location has been updated correctly.
        """

        location_data = {
            "country": "Test Country",
            "city": "Updated first city",
            "post_code": "18505",
            "street": "Updated street",
            "house_number": "3/4"
        }

        response = self.client.put(self.placement_location_retrieve_update_url(self.inactive_placement.pk),
                                   location_data,
                                   fromat="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["city"], "Updated first city")
        self.assertEqual(response.data["post_code"], "18505")
        self.assertEqual(response.data["street"], "Updated street")
        self.assertEqual(response.data["house_number"], "3/4")

    def test_user_owner_cannot_delete_location(self):
        """
        Test if owner user cannot delete Placement Location.
        Sends a DELETE request a and expects 405 METHOD NOT ALLOWED response.
        Verifies that the Placement Location hasn't been deleted.
        """

        response = self.client.delete(self.placement_location_retrieve_update_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(response.data["detail"], "Method \"DELETE\" not allowed.")
        self.assertTrue(PlacementLocation.related_objects.get(placement=self.placement.pk))

    def test_unauthorized_user_owner_cannot_retrieve_location(self):
        """
        Test if unauthorized owner user cannot retrieve Placement Location.
        Sends a GET request and expects 401 UNAUTHORIZED response.
        Verifies that the user receive the correct answer.
        """

        self.client.cookies.clear()

        response = self.client.get(self.placement_location_retrieve_update_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")

    def test_unauthorized_user_owner_cannot_update_location(self):
        """
        Test if unauthorized owner user cannot update Placement Location.
        Sends a PUT request with new data and expects 401 UNAUTHORIZED response.
        Verifies that the Placement Location hasn't been updated.
        """

        location_data = {
            "country": "Test Country",
            "city": "Updated first city",
            "post_code": "18505",
            "street": "Updated street",
            "house_number": "3/4"
        }

        self.client.cookies.clear()

        response = self.client.put(self.placement_location_retrieve_update_url(self.placement.pk), location_data,
                                   fromat="json")

        placement_location = PlacementLocation.related_objects.get(placement=self.placement.pk)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")
        self.assertEqual(placement_location.city, self.placement_location.city)
        self.assertEqual(placement_location.post_code, self.placement_location.post_code)
        self.assertEqual(placement_location.street, self.placement_location.street)
        self.assertEqual(placement_location.house_number, self.placement_location.house_number)

    def test_another_landlord_user_cannot_retrieve_location(self):
        """
        Test if another Landlord user cannot retrieve Placement Location.
        Sends a GET request and expects 403 FORBIDDEN response.
        Verifies that the user receive the correct answer.
        """

        refresh = RefreshToken.for_user(self.landlord_user2)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.get(self.placement_location_retrieve_update_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")

    def test_another_landlord_cannot_update_location(self):
        """
        Test if another Landlord user cannot update Placement Location.
        Sends a PUT request with new data and expects 403 FORBIDDEN response.
        Verifies that the Placement Location hasn't been updated.
        """

        location_data = {
            "country": "Test Country",
            "city": "Updated first city",
            "post_code": "18505",
            "street": "Updated street",
            "house_number": "3/4"
        }

        refresh = RefreshToken.for_user(self.landlord_user2)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.put(self.placement_location_retrieve_update_url(self.placement.pk), location_data,
                                   fromat="json")

        placement_location = PlacementLocation.related_objects.get(placement=self.placement.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertEqual(placement_location.city, self.placement_location.city)
        self.assertEqual(placement_location.post_code, self.placement_location.post_code)
        self.assertEqual(placement_location.street, self.placement_location.street)
        self.assertEqual(placement_location.house_number, self.placement_location.house_number)

    def test_regular_user_cannot_retrieve_location(self):
        """
        Test if regular user cannot retrieve Placement Location.
        Sends a GET request and expects 403 FORBIDDEN response.
        Verifies that the user receive the correct answer.
        """

        refresh = RefreshToken.for_user(self.regular_user)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.get(self.placement_location_retrieve_update_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")

    def test_regular_user_cannot_update_location(self):
        """
        Test if regular user cannot update Placement Location.
        Sends a PUT request with new data and expects 403 FORBIDDEN response.
        Verifies that the Placement Location hasn't been updated.
        """

        location_data = {
            "country": "Test Country",
            "city": "Updated first city",
            "post_code": "18505",
            "street": "Updated street",
            "house_number": "3/4"
        }

        refresh = RefreshToken.for_user(self.regular_user)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.put(self.placement_location_retrieve_update_url(self.placement.pk), location_data,
                                   fromat="json")

        placement_location = PlacementLocation.related_objects.get(placement=self.placement.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertEqual(placement_location.city, self.placement_location.city)
        self.assertEqual(placement_location.post_code, self.placement_location.post_code)
        self.assertEqual(placement_location.street, self.placement_location.street)
        self.assertEqual(placement_location.house_number, self.placement_location.house_number)
