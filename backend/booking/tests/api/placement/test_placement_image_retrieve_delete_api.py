import os
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from booking.models import PlacementImage
from booking.tests.api.placement.placement_setup import PlacementSetup


class PlacementDetailsRetrieveUpdateTest(PlacementSetup):
    def test_user_owner_can_retrieve_images(self):
        """
        Test if owner user can retrieve Placement Images list.
        Sends a GET request and expects 200 OK response.
        Verifies that the Placement Images have the correct link to the Placement.
        """

        response = self.client.get(self.placement_image_retrieve_delete_url(self.placement.pk))

        placement_image = PlacementImage.objects.filter(placement=self.placement.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["images"]), placement_image.count())
        self.assertEqual([image["placement"] for image in response.data["images"]],
                         [image.placement.pk for image in placement_image])

    def test_user_owner_can_retrieve_images_from_inactive_placement(self):
        """
        Test if owner user can retrieve Placement Images list from Inactive Placement.
        Sends a GET request and expects 200 OK response.
        Verifies that the Placement Images have the correct link to the Placement.
        """

        response = self.client.get(self.placement_image_retrieve_delete_url(self.inactive_placement.pk))

        placement_image = PlacementImage.objects.filter(placement=self.inactive_placement.pk)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["images"]), placement_image.count())
        self.assertEqual([image["placement"] for image in response.data["images"]],
                         [image.placement.pk for image in placement_image])

    def test_user_owner_can_add_images(self):
        """
        Test if owner user can add new Placement Images.
        Sends a POST request with images and expects 201 CREATED response.
        Verifies that the Placement Images have been uploaded and have the correct link to the Placement.
        """

        images_data = {
            "uploaded_images": [image for image in self.add_temp_images_set1]
        }

        response = self.client.post(self.placement_image_retrieve_delete_url(self.placement.pk), images_data,
                                    format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PlacementImage.objects.filter(placement=self.placement.pk).count(), 15)

    def test_user_owner_can_add_images_to_inactive_placement(self):
        """
        Test if owner user can add new Placement Images to Inactive Placement.
        Sends a POST request with images and expects 201 CREATED response.
        Verifies that the Placement Images have been uploaded and have the correct link to the Placement.
        """

        images_data = {
            "uploaded_images": [image for image in self.add_temp_images_set1]
        }

        response = self.client.post(self.placement_image_retrieve_delete_url(self.inactive_placement.pk), images_data,
                                    format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PlacementImage.objects.filter(placement=self.inactive_placement.pk).count(), 15)

    def test_user_owner_cannot_add_too_many_images(self):
        """
        Test if owner user cannot add too many Images.
        Sends a POST request with images and expects 400 BAD REQUEST response.
        Verifies that the Placement Images have not been uploaded and the user received correct answer.
        """

        images_data = {
            "uploaded_images": [image for image in self.temp_images_set1]
        }

        response = self.client.post(self.placement_image_retrieve_delete_url(self.placement.pk), images_data,
                                    format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["uploaded_images"][0], "You can add only 7 more image(s).")
        self.assertEqual(len(self.placement_images), PlacementImage.objects.filter(placement=self.placement.pk).count())

    def test_user_owner_retrieve_correct_response_when_images_limit_is_reached(self):
        """
        Test if owner getting the correct answer when the images limit is reached.
        Sends the first POST request with images and expects 201 CREATED response.
        Verifies that the Placement Images have been uploaded.
        """

        images_data = {
            "uploaded_images": [image for image in self.add_temp_images_set1]
        }

        first_response = self.client.post(self.placement_image_retrieve_delete_url(self.placement.pk), images_data,
                                          format="multipart")

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PlacementImage.objects.filter(placement=self.placement.pk).count(), 15)

        """
        Sends the second POST request with images and expects 400 BAD REQUEST response.
        Verifies that the Placement Images have not been uploaded and the user received correct answer.
        """

        images_data = {
            "uploaded_images": [image for image in self.temp_images_set1]
        }

        second_response = self.client.post(self.placement_image_retrieve_delete_url(self.placement.pk), images_data,
                                           format="multipart")

        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(second_response.data["uploaded_images"][0], "You have reached your image limit.")

    def test_user_owner_cannot_add_too_heavy_image(self):
        """
        Test if owner user cannot add too heavy Image.
        Sends a POST request with images and expects 400 BAD REQUEST response.
        Verifies that the Placement Images have not been uploaded and the user received correct answer.
        """

        image_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "image/test_image.jpg"))

        with open(image_path, "rb") as file:
            image = SimpleUploadedFile("test_image.jpg", file.read(), content_type="image/jpeg")

        images_data = {
            "uploaded_images": [image]
        }

        response = self.client.post(self.placement_image_retrieve_delete_url(self.placement.pk), images_data,
                                    format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["uploaded_images"][0], "Each image must be smaller than 10 MB.")
        self.assertEqual(PlacementImage.objects.filter(placement=self.placement.pk).count(), len(self.placement_images))

    def test_user_owner_can_delete_images(self):
        """
        Test if owner user can delete the Placement Images.
        Sends a DELETE request and expects 204 NO CONTENT response.
        Verifies that the Placement Images have been deleted.
        """

        image_data = {
            "image_list": [image.pk for image in PlacementImage.objects.filter(placement=self.placement.pk)]
        }

        response = self.client.delete(self.placement_image_retrieve_delete_url(self.placement.pk), image_data,
                                      format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data["detail"], "Successfully deleted 8 image(s).")
        self.assertFalse(PlacementImage.objects.filter(placement=self.placement.pk))

    def test_user_owner_can_delete_images_in_inactive_placement(self):
        """
        Test if owner user can delete the Placement Images in Inactive Placement.
        Sends a DELETE request and expects 204 NO CONTENT response.
        Verifies that the Placement Images have been deleted.
        """

        image_data = {
            "image_list": [image.pk for image in PlacementImage.objects.filter(placement=self.inactive_placement.pk)]
        }

        response = self.client.delete(self.placement_image_retrieve_delete_url(self.inactive_placement.pk), image_data,
                                      format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.data["detail"], "Successfully deleted 8 image(s).")
        self.assertFalse(PlacementImage.objects.filter(placement=self.inactive_placement.pk))

    def test_unauthorized_user_owner_cannot_retrieve_images(self):
        """
        Test if unauthorized owner user cannot retrieve Placement Images.
        Sends a GET request and expects 401 UNAUTHORIZED response.
        Verifies that the user receive the correct answer.
        """

        self.client.cookies.clear()

        response = self.client.get(self.placement_image_retrieve_delete_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")

    def test_unauthorized_user_owner_cannot_add_images(self):
        """
        Test if unauthorized owner user cannot add Images.
        Sends a POST request with images and expects 401 UNAUTHORIZED response.
        Verifies that the Placement Images have not been uploaded and the user received correct answer.
        """

        images_data = {
            "uploaded_images": [image for image in self.add_temp_images_set1]
        }

        self.client.cookies.clear()

        response = self.client.post(self.placement_image_retrieve_delete_url(self.placement.pk), images_data,
                                    format="multipart")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")
        self.assertEqual(PlacementImage.objects.filter(placement=self.placement.pk).count(), len(self.placement_images))

    def test_unauthorized_user_owner_cannot_delete_images(self):
        """
        Test if unauthorized owner user cannot delete Images.
        Sends a DELETE request and expects 401 UNAUTHORIZED response.
        Verifies that the Placement Images have not been deleted and user receive the correct answer.
        """

        image_data = {
            "image_list": [image.pk for image in PlacementImage.objects.filter(placement=self.placement.pk)]
        }

        self.client.cookies.clear()

        response = self.client.delete(self.placement_image_retrieve_delete_url(self.placement.pk), image_data,
                                      format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")
        self.assertEqual(PlacementImage.objects.filter(placement=self.placement.pk).count(), len(self.placement_images))

    def test_another_landlord_user_cannot_retrieve_images(self):
        """
        Test if another landlord user cannot retrieve Placement Images.
        Sends a GET request and expects 403 FORBIDDEN response.
        Verifies that the user receive the correct answer.
        """

        refresh = RefreshToken.for_user(self.landlord_user2)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.get(self.placement_image_retrieve_delete_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")

    def test_another_landlord_user_cannot_add_images(self):
        """
        Test if another landlord user cannot add new Placement Images.
        Sends a POST request with images and expects 403 FORBIDDEN response.
        Verifies that the Placement Images have not been uploaded and the user received correct answer.
        """

        images_data = {
            "uploaded_images": [image for image in self.add_temp_images_set1]
        }

        refresh = RefreshToken.for_user(self.landlord_user2)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.post(self.placement_image_retrieve_delete_url(self.placement.pk), images_data,
                                    format="multipart")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertEqual(PlacementImage.objects.filter(placement=self.placement.pk).count(), len(self.placement_images))

    def test_another_landlord_user_cannot_delete_images(self):
        """
        Test if another landlord user cannot delete Placement Images.
        Sends a DELETE request and expects 403 FORBIDDEN response.
        Verifies that the Placement Images have not been deleted and user receive the correct answer.
        """

        refresh = RefreshToken.for_user(self.landlord_user2)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        image_data = {
            "image_list": [image.pk for image in PlacementImage.objects.filter(placement=self.placement.pk)]
        }

        response = self.client.delete(self.placement_image_retrieve_delete_url(self.placement.pk), image_data,
                                      format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertEqual(PlacementImage.objects.filter(placement=self.placement.pk).count(), len(self.placement_images))

    def test_regular_user_cannot_retrieve_images(self):
        """
        Test if regular user cannot retrieve Placement Images.
        Sends a GET request and expects 403 FORBIDDEN response.
        Verifies that the user receive the correct answer.
        """

        refresh = RefreshToken.for_user(self.regular_user)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.get(self.placement_image_retrieve_delete_url(self.placement.pk))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")

    def test_regular_user_cannot_add_images(self):
        """
        Test if regular user cannot add new Placement Images.
        Sends a POST request with images and expects 403 FORBIDDEN response.
        Verifies that the Placement Images have not been uploaded and the user received correct answer.
        """

        images_data = {
            "uploaded_images": [image for image in self.add_temp_images_set1]
        }

        refresh = RefreshToken.for_user(self.regular_user)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.post(self.placement_image_retrieve_delete_url(self.placement.pk), images_data,
                                    format="multipart")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertEqual(PlacementImage.objects.filter(placement=self.placement.pk).count(), len(self.placement_images))

    def test_regular_user_cannot_delete_images(self):
        """
        Test if regular user cannot delete Placement Images.
        Sends a DELETE request and expects 403 FORBIDDEN response.
        Verifies that the Placement Images have not been deleted and user receive the correct answer.
        """

        refresh = RefreshToken.for_user(self.regular_user)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        image_data = {
            "image_list": [image.pk for image in PlacementImage.objects.filter(placement=self.placement.pk)]
        }

        response = self.client.delete(self.placement_image_retrieve_delete_url(self.placement.pk), image_data,
                                      format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertEqual(PlacementImage.objects.filter(placement=self.placement.pk).count(), len(self.placement_images))
