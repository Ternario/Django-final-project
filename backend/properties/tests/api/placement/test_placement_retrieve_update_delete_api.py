from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from properties.models import Placement, PlacementImage, PlacementDetails, PlacementLocation, User
from properties.tests.api.placement.placement_setup import PlacementSetup


class PlacementRetrieveUpdateDeleteTest(PlacementSetup):

    def test_unauthenticated_user_can_retrieve_full_info_about_placement(self):
        """
        Test if unauthenticated user can retrieve the active Placement by id.
        Sends a GET request with id and expects a 200 OK response.
        Verifies that the user receive the correct linked placement data.
        """

        self.client.cookies.clear()

        response = self.client.get(self.placement_retrieve_update_delete_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.placement.pk)
        self.assertEqual(response.data["category_name"], self.hotel_category.name)
        self.assertEqual(response.data["placement_location"]["placement"], self.placement.pk)
        self.assertEqual(response.data["placement_details"]["placement"], self.placement.pk)
        self.assertEqual(response.data["placement_images"][0]["placement"], self.placement.pk)
        self.assertEqual(len(response.data["placement_images"]), len(self.placement_images))

    def test_authenticated_user_can_retrieve_full_info_about_placement(self):
        """
        Test if authenticated user can retrieve the active Placement by id.
        Sends a GET request with id and expects a 200 OK response.
        Verifies that the user receive the correct linked placement data.
        """

        refresh = RefreshToken.for_user(self.regular_user)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.get(self.placement_retrieve_update_delete_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.placement.pk)
        self.assertEqual(response.data["category_name"], self.hotel_category.name)
        self.assertEqual(response.data["placement_location"]["placement"], self.placement.pk)
        self.assertEqual(response.data["placement_details"]["placement"], self.placement.pk)
        self.assertEqual(response.data["placement_images"][0]["placement"], self.placement.pk)
        self.assertEqual(len(response.data["placement_images"]), len(self.placement_images))

    def test_user_owner_can_retrieve_full_info_about_placement(self):
        """
        Test if owner user can retrieve the active Placement by id.
        Sends a GET request with id and expects a 200 OK response.
        Verifies that the user receive the correct linked placement data.
        """

        response = self.client.get(self.placement_retrieve_update_delete_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.placement.pk)
        self.assertEqual(response.data["category_name"], self.hotel_category.name)
        self.assertEqual(response.data["placement_location"]["placement"], self.placement.pk)
        self.assertEqual(response.data["placement_details"]["placement"], self.placement.pk)
        self.assertEqual(response.data["placement_images"][0]["placement"], self.placement.pk)
        self.assertEqual(len(response.data["placement_images"]), len(self.placement_images))

    def test_user_owner_can_update_placement(self):
        """
        Test if owner user can update Placement.
        Sends a PUT request with new data and expects 200 OK response.
        Verifies that the Placement has been updated correctly.
        """

        placement_data = {
            "category": self.hostel_category.id,
            "title": "Another Hostel by Landlord User",
            "description": "A" * 90,
            "price": 345,
            "number_of_rooms": 3,
            "placement_area": 60,
            "total_beds": 4,
            "single_bed": 3,
            "double_bed": 1,
        }

        response = self.client.put(self.placement_retrieve_update_delete_url(self.placement.pk), placement_data,
                                   format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["category_name"], self.hostel_category.name)
        self.assertEqual(response.data["title"], "Another Hostel by Landlord User")
        self.assertEqual(response.data["description"], "A" * 90)
        self.assertEqual(float(response.data["price"]), 345.00)
        self.assertEqual(response.data["number_of_rooms"], 3)
        self.assertEqual(float(response.data["placement_area"]), 60.00)
        self.assertEqual(response.data["total_beds"], 4)
        self.assertEqual(response.data["single_bed"], 3)
        self.assertEqual(response.data["double_bed"], 1)

    def test_user_owner_can_delete_placement(self):
        """
        Test if owner user can delete a Placement.
        Sends a DELETE request and expects 204 NO CONTENT response.
        Verifies that the Placement and all linked objects have been deleted.
        """

        response = self.client.delete(self.placement_retrieve_update_delete_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Placement.deleted_objects.count(), 1)
        self.assertFalse(PlacementImage.related_objects.filter(placement=self.placement.pk))
        self.assertFalse(PlacementDetails.related_objects.filter(placement=self.placement.pk))
        self.assertFalse(PlacementLocation.related_objects.filter(placement=self.placement.pk))

    def test_unauthorized_owner_user_cannot_update_placement(self):
        """
        Test if unauthorized owner user cannot update Placement.
        Sends a PUT request with new data and expects 401 UNAUTHORIZED response.
        Verifies that the Placement hasn't been updated.
        """

        placement_data = {
            "category": self.hostel_category.id,
            "title": "Another Hostel by Landlord User",
            "description": "A" * 90,
            "price": 345,
            "number_of_rooms": 3,
            "placement_area": 60,
            "total_beds": 4,
            "single_bed": 3,
            "double_bed": 1,
        }

        self.client.cookies.clear()

        response = self.client.put(self.placement_retrieve_update_delete_url(self.placement.pk), placement_data,
                                   format="json")

        placement = Placement.objects.get(pk=self.placement.pk)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")
        self.assertEqual(placement.category, self.placement.category)
        self.assertEqual(placement.title, self.placement.title)
        self.assertEqual(placement.price, self.placement.price)
        self.assertEqual(placement.placement_area, self.placement.placement_area)
        self.assertEqual(placement.total_beds, self.placement.total_beds)

    def test_unauthorized_owner_user_cannot_delete_placement(self):
        """
        Test if unauthorized owner user cannot delete a Placement.
        Sends a DELETE request and expects 401 UNAUTHORIZED response.
        Verifies that tha Placement and all linked objects have not been deleted.
        """

        self.client.cookies.clear()

        response = self.client.delete(self.placement_retrieve_update_delete_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")
        self.assertEqual(Placement.deleted_objects.count(), 0)
        self.assertEqual(PlacementImage.related_objects.filter(placement=self.placement.pk).count(), 8)
        self.assertTrue(PlacementDetails.related_objects.get(placement=self.placement.pk))
        self.assertTrue(PlacementLocation.related_objects.get(placement=self.placement.pk))

    def test_another_landlord_user_cannot_update_placement(self):
        """
        Test if another Landlord user cannot update Placement.
        Sends a PUT request with new data and expects 403 FORBIDDEN response.
        Verifies that the Placement hasn't been updated.
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

        refresh = RefreshToken.for_user(self.landlord_user2)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.put(self.placement_retrieve_update_delete_url(self.placement.pk), placement_data,
                                   format="json")

        placement = Placement.objects.get(pk=self.placement.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertEqual(placement.title, self.placement.title)
        self.assertEqual(placement.price, self.placement.price)
        self.assertEqual(placement.placement_area, self.placement.placement_area)

    def test_another_landlord_user_cannot_delete_placement(self):
        """
        Test if another Landlord user cannot delete a Placement.
        Sends a DELETE request and expects 403 FORBIDDEN response.
        Verifies that tha Placement and all linked objects have not been deleted.
        """

        refresh = RefreshToken.for_user(self.landlord_user2)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.delete(self.placement_retrieve_update_delete_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertEqual(Placement.deleted_objects.count(), 0)
        self.assertEqual(PlacementImage.related_objects.filter(placement=self.placement.pk).count(), 8)
        self.assertTrue(PlacementDetails.related_objects.get(placement=self.placement.pk))
        self.assertTrue(PlacementLocation.related_objects.get(placement=self.placement.pk))

    def test_regular_user_cannot_update_placement(self):
        """
        Test if regular user cannot update Placement.
        Sends a PUT request with new data and expects 403 FORBIDDEN response.
        Verifies that the Placement hasn't been updated.
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

        refresh = RefreshToken.for_user(self.regular_user)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.put(self.placement_retrieve_update_delete_url(self.placement.pk), placement_data,
                                   format="json")

        placement = Placement.objects.get(pk=self.placement.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertEqual(placement.title, self.placement.title)
        self.assertEqual(placement.price, self.placement.price)
        self.assertEqual(placement.placement_area, self.placement.placement_area)

    def test_regular_user_cannot_delete_placement(self):
        """
        Test if regular user cannot delete a Placement.
        Sends a DELETE request and expects 403 FORBIDDEN response.
        Verifies that tha Placement and all linked objects have not been deleted.
        """

        refresh = RefreshToken.for_user(self.regular_user)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.delete(self.placement_retrieve_update_delete_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertEqual(Placement.deleted_objects.count(), 0)
        self.assertEqual(PlacementImage.related_objects.filter(placement=self.placement.pk).count(), 8)
        self.assertTrue(PlacementDetails.related_objects.get(placement=self.placement.pk))
        self.assertTrue(PlacementLocation.related_objects.get(placement=self.placement.pk))

#         add test to second delete the same placement
