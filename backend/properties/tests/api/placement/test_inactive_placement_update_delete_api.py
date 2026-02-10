from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from properties.models import Placement, PlacementImage, PlacementDetails, PlacementLocation
from properties.tests.api.placement.placement_setup import PlacementSetup


class InactivePlacementRetrieveUpdateDeleteTest(PlacementSetup):
    def test_user_owner_can_retrieve_full_info_about_inactive_placement(self):
        """
        Test if user owner can retrieve the inactive Placement by id.
        Sends a GET request with id and expects a 200 OK response.
        Verifies that the user receive the correct linked placement data.
        """

        response = self.client.get(self.inactive_placement_retrieve_update_delete_url(self.inactive_placement.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.inactive_placement.pk)
        self.assertEqual(response.data["category_name"], self.hostel_category.name)
        self.assertEqual(response.data["placement_location"]["placement"], self.inactive_placement.pk)
        self.assertEqual(response.data["placement_details"]["placement"], self.inactive_placement.pk)
        self.assertEqual(response.data["placement_images"][0]["placement"], self.inactive_placement.pk)
        self.assertEqual(len(response.data["placement_images"]), len(self.inactive_placement_images))

    def test_user_owner_can_update_inactive_placement(self):
        """
        Test if owner user can update inactive Placement.
        Sends a PUT request with new data and expects 200 OK response.
        Verifies that the Placement has been updated correctly.
        """

        placement_data = {
            "category": self.hotel_category.id,
            "title": "Another Hotel by Landlord User",
            "description": "A" * 90,
            "price": 345,
            "number_of_rooms": 3,
            "placement_area": 60,
            "total_beds": 4,
            "single_bed": 3,
            "double_bed": 1,
        }

        response = self.client.put(self.inactive_placement_retrieve_update_delete_url(self.inactive_placement.pk),
                                   placement_data,
                                   format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["category_name"], self.hotel_category.name)
        self.assertEqual(response.data["title"], "Another Hotel by Landlord User")
        self.assertEqual(response.data["description"], "A" * 90)
        self.assertEqual(float(response.data["price"]), 345.00)
        self.assertEqual(response.data["number_of_rooms"], 3)
        self.assertEqual(float(response.data["placement_area"]), 60.00)
        self.assertEqual(response.data["total_beds"], 4)
        self.assertEqual(response.data["single_bed"], 3)
        self.assertEqual(response.data["double_bed"], 1)

    def test_user_owner_can_delete_inactive_placement(self):
        """
        Test if owner user can delete inactive Placement.
        Sends a DELETE request and expects 204 NO CONTENT response.
        Verifies that the Placement and all linked objects have been deleted.
        """

        response = self.client.delete(self.inactive_placement_retrieve_update_delete_url(self.inactive_placement.pk))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Placement.deleted_objects.count(), 1)
        self.assertFalse(PlacementImage.related_objects.filter(placement=self.inactive_placement.pk))
        self.assertFalse(PlacementDetails.related_objects.filter(placement=self.inactive_placement.pk))
        self.assertFalse(PlacementLocation.related_objects.filter(placement=self.inactive_placement.pk))

    def test_unauthorized_user_owner_cannot_retrieve_full_info_about_inactive_placement(self):
        """
        Test if unauthorized user owner cannot retrieve the inactive Placement by id.
        Sends a GET request with id and expects 401 UNAUTHORIZED response.
        Verifies that the user receive the correct answer.
        """

        self.client.cookies.clear()

        response = self.client.get(self.inactive_placement_retrieve_update_delete_url(self.inactive_placement.pk))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")

    def test_unauthorized_owner_user_cannot_update_inactive_placement(self):
        """
        Test if unauthorized owner user cannot update inactive Placement.
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

        response = self.client.put(self.inactive_placement_retrieve_update_delete_url(self.inactive_placement.pk),
                                   placement_data,
                                   format="json")

        placement = Placement.inactive_objects.get(pk=self.inactive_placement.pk)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")
        self.assertEqual(placement.category, self.inactive_placement.category)
        self.assertEqual(placement.title, self.inactive_placement.title)
        self.assertEqual(placement.price, self.inactive_placement.price)
        self.assertEqual(placement.placement_area, self.inactive_placement.placement_area)
        self.assertEqual(placement.total_beds, self.inactive_placement.total_beds)

    def test_unauthorized_owner_user_cannot_delete_inactive_placement(self):
        """
        Test if unauthorized owner user can delete inactive Placement.
        Sends a DELETE request and expects 401 UNAUTHORIZED response.
        Verifies that tha Placement and all linked objects have not been deleted.
        """

        self.client.cookies.clear()

        response = self.client.delete(self.inactive_placement_retrieve_update_delete_url(self.inactive_placement.pk))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")
        self.assertEqual(Placement.deleted_objects.count(), 0)
        self.assertEqual(PlacementImage.related_objects.filter(placement=self.inactive_placement.pk).count(), 8)
        self.assertTrue(PlacementDetails.related_objects.get(placement=self.inactive_placement.pk))
        self.assertTrue(PlacementLocation.related_objects.get(placement=self.inactive_placement.pk))

    def test_another_landlord_user_cannot_retrieve_full_info_about_inactive_placement(self):
        """
        Test if another landlord user cannot retrieve the inactive Placement by id.
        Sends a GET request with id and expects 403 FORBIDDEN response.
        Verifies that the user receive the correct answer.
        """

        refresh = RefreshToken.for_user(self.landlord_user2)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.get(self.inactive_placement_retrieve_update_delete_url(self.inactive_placement.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")

    def test_another_landlord_user_cannot_update_inactive_placement(self):
        """
        Test if another landlord user cannot update inactive Placement.
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

        response = self.client.put(self.inactive_placement_retrieve_update_delete_url(self.inactive_placement.pk),
                                   placement_data,
                                   format="json")

        placement = Placement.inactive_objects.get(pk=self.inactive_placement.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertEqual(placement.title, self.inactive_placement.title)
        self.assertEqual(placement.price, self.inactive_placement.price)
        self.assertEqual(placement.placement_area, self.inactive_placement.placement_area)

    def test_another_landlord_user_cannot_delete_inactive_placement(self):
        """
        Test if another landlord user cannot delete inactive Placement.
        Sends a DELETE request and expects 403 FORBIDDEN response.
        Verifies that tha Placement and all linked objects have not been deleted.
        """

        refresh = RefreshToken.for_user(self.landlord_user2)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.delete(self.inactive_placement_retrieve_update_delete_url(self.inactive_placement.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertEqual(Placement.deleted_objects.count(), 0)
        self.assertEqual(PlacementImage.related_objects.filter(placement=self.inactive_placement.pk).count(), 8)
        self.assertTrue(PlacementDetails.related_objects.get(placement=self.inactive_placement.pk))
        self.assertTrue(PlacementLocation.related_objects.get(placement=self.inactive_placement.pk))

    def test_regular_user_cannot_retrieve_full_info_about_inactive_placement(self):
        """
        Test if regular user cannot retrieve the inactive Placement by id.
        Sends a GET request with id and expects 403 FORBIDDEN response.
        Verifies that the user receive the correct linked placement data.
        """

        refresh = RefreshToken.for_user(self.regular_user)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.get(self.inactive_placement_retrieve_update_delete_url(self.inactive_placement.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")

    def test_regular_user_cannot_update_inactive_placement(self):
        """
        Test if regular user cannot update inactive Placement.
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

        response = self.client.put(self.inactive_placement_retrieve_update_delete_url(self.inactive_placement.pk),
                                   placement_data,
                                   format="json")

        placement = Placement.inactive_objects.get(pk=self.inactive_placement.pk)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertEqual(placement.title, self.inactive_placement.title)
        self.assertEqual(placement.price, self.inactive_placement.price)
        self.assertEqual(placement.placement_area, self.inactive_placement.placement_area)

    def test_regular_user_cannot_delete_inactive_placement(self):
        """
        Test if regular user cannot delete inactive Placement.
        Sends a DELETE request and expects 403 FORBIDDEN response.
        Verifies that tha Placement and all linked objects have not been deleted.
        """

        refresh = RefreshToken.for_user(self.regular_user)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.delete(self.inactive_placement_retrieve_update_delete_url(self.inactive_placement.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertEqual(Placement.deleted_objects.count(), 0)
        self.assertEqual(PlacementImage.related_objects.filter(placement=self.inactive_placement.pk).count(), 8)
        self.assertTrue(PlacementDetails.related_objects.get(placement=self.inactive_placement.pk))
        self.assertTrue(PlacementLocation.related_objects.get(placement=self.inactive_placement.pk))
