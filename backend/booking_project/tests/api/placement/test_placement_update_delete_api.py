from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from booking_project.models import Placement, PlacementImage, PlacementDetails, PlacementLocation
from booking_project.tests.api.placement.placement_setup import PlacementSetup


class PlacementRetrieveUpdateDeleteTest(PlacementSetup):

    def test_user_retrieve_active_placement_list(self):
        """
        Test if user can retrieve active Placement list.
        Sends a Get request and expects a 200 OK response.
        Verifies that the number of retrieved placement and all active Placements are the same.
        """

        response = self.client.get(self.placement_active_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Placement.objects.all().count(), 1)

    def test_user_can_retrieve_full_info_about_placement(self):
        """
        Test if user can retrieve active Placement by id.
        Sends a GET request with id and expects a 200 OK response.
        Verifies that the user receive the correct linked placement data.
        """

        response = self.client.get(self.placement_retrieve_update_delete_url(1))

        self.assertEqual(response.data["id"], 1)
        self.assertEqual(response.data["category_name"], self.hotel_category.name)
        self.assertEqual(response.data["placement_location"]["placement"], 1)
        self.assertEqual(response.data["placement_details"]["placement"], 1)
        self.assertEqual(response.data["placement_image"][0]["placement"], 1)
        self.assertEqual(len(response.data["placement_image"]), 8)

    def test_user_owner_can_update_placement(self):
        """
        Test if owner user can update Placement.
        Sends a PUT request with new data and expects 200 OK response.
        Verifies that the placement has been updated correctly.
        """

        placement_data = {
            "category": self.hostel_category.id,
            "title": "Second Hostel by Landlord User",
            "description": "A" * 90,
            "price": 345,
            "number_of_rooms": 3,
            "placement_area": 60,
            "total_beds": 4,
            "single_bed": 3,
            "double_bed": 1,
        }

        response = self.client.put(self.placement_retrieve_update_delete_url(1), placement_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["category_name"], self.hostel_category.name)
        self.assertEqual(response.data["title"], "Second Hostel by Landlord User")
        self.assertEqual(response.data["description"], "A" * 90)
        self.assertEqual(float(response.data["price"]), 345.00)
        self.assertEqual(response.data["number_of_rooms"], 3)
        self.assertEqual(float(response.data["placement_area"]), 60.00)
        self.assertEqual(response.data["total_beds"], 4)
        self.assertEqual(response.data["single_bed"], 3)
        self.assertEqual(response.data["double_bed"], 1)

    def test_user_owner_can_deactivate_placement(self):
        """
        Test if owner user can deactivate Placement.
        Sends a PATCH request with data and expects 200 OK response.
        Verifies that the placement has been updated correctly.
        """

        placement_data = {
            "activate": False
        }

        response = self.client.patch(self.placement_activation(1), placement_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Placement.objects.count(), 0)
        self.assertFalse(Placement.all_objects.get(pk=1).is_active)

    def test_user_owner_can_activate_placement(self):
        """
        Test if owner user can activate Placement.
        Sends a PATCH request with data and expects 200 OK response.
        Verifies that the placement has been updated correctly.
        """

        placement_data = {
            "activate": True
        }

        response = self.client.patch(self.placement_activation(2), placement_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Placement.objects.count(), 2)
        self.assertTrue(Placement.objects.get(pk=2).is_active)

    def test_user_owner_cannot_activate_placement_without_images(self):
        """
        Test if owner user cannot activate Placement without images.
        Sends a PATCH request with data and expects 400 BAD REQUEST response.
        Verifies that the placement hasn't been activated.
        """

        PlacementImage.objects.filter(placement=2).delete()

        placement_data = {
            "activate": True
        }

        response = self.client.patch(self.placement_activation(2), placement_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["activate"][0], "You need to fill in the placement details or add photos.")
        self.assertEqual(Placement.objects.count(), 1)
        self.assertFalse(Placement.all_objects.get(pk=2).is_active)

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

        first_response = self.client.put(self.placement_details_retrieve_update_url(2), details_data, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        """
        Sends the second PATCH request with data and expects 400 BAD REQUEST response.
        Verifies that the placement hasn't been activated.
        """

        placement_data = {
            "activate": True
        }

        second_response = self.client.patch(self.placement_activation(2), placement_data, format="json")

        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(second_response.data["activate"][0],
                         "You need to fill in the placement details or add photos.")
        self.assertEqual(Placement.objects.count(), 1)
        self.assertFalse(Placement.all_objects.get(pk=2).is_active)

    def test_owner_user_can_delete_placement(self):
        """
        Test if owner user can delete a Placement.
        Sends a DELETE request and expects 204 NO CONTENT response.
        Verifies that tha placement and all linked objects has been deleted.
        """

        response = self.client.delete(self.placement_retrieve_update_delete_url(1))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Placement.deleted_objects.count(), 1)
        self.assertFalse(PlacementImage.objects.filter(placement=1))
        self.assertFalse(PlacementDetails.objects.filter(placement=1))
        self.assertFalse(PlacementLocation.objects.filter(placement=1))

    # def test_user_cannot_update_placement(self):
    #     """
    #     Test is owner user can update Placement.
    #     Sends a PUT request with new data and expects 200 OK response.
    #     Verifies that the placement has been updated correctly.
    #     """
    #
    #     placement_data = {
    #         "category": self.hostel_category.id,
    #         "title": "Second Hostel by Landlord User",
    #         "description": "A" * 90,
    #         "price": 345,
    #         "number_of_rooms": 3,
    #         "placement_area": 60,
    #         "total_beds": 4,
    #         "single_bed": 3,
    #         "double_bed": 1,
    #     }
    #
    #     refresh = RefreshToken.for_user(self.regular_user)
    #
    #     self.client.cookies["access_token"] = str(refresh.access_token)
    #     self.client.cookies["refresh_token"] = str(refresh)
    #
    #     response = self.client.put(self.placement_retrieve_update_delete_url(1), placement_data, format="json")
    #     print(response.data)

    # def test_user_retrieve_placement_list_by_city(self):
    #     """
    #     Test if user can retrieve the list of active placements according to the city query parameters.
    #     Sends a Get request and expects a 200 OK response.
    #     Verifies that the number of retrieved placement and all active Placements are the same.
    #     """
    #     response = self.client.get(self.placement_active_list_url, data={"city": "Test city"})
    #
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(len(response.data), 1)
    #     self.assertEqual(Placement.objects.filter(placement_location__city="Test city").count(), 1)
