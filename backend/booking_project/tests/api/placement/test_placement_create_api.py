from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from booking_project.models import Placement, PlacementDetails, PlacementLocation, PlacementImage
from booking_project.tests.api.placement.placement_setup import PlacementSetup


class PlacementCreateTest(PlacementSetup):
    def test_landlord_user_can_create_placement(self):
        """
        Test if landlord user can create and activate new Placement.
        Sends first POST request with placement and placement location data and expects a 201 CREATED response.
        Verifies that the placement and placement location count increases and the new placement
        has the correct title and link to user and category, placement location has correct link to placement.
        Also verifies if placement details count increases and has correct link to placement.
        """

        placement_data = {
            "placement_location": {
                "country": "Germany",
                "city": "Berlin",
                "post_code": "34567",
                "street": "Test street",
                "house_number": "4"
            },
            "category": self.hotel_category.id,
            "title": "Another Hotel by Landlord User",
            "description": "A" * 60,
            "price": 123,
            "number_of_rooms": 2,
            "placement_area": 40,
            "total_beds": 2,
            "single_bed": 1,
            "double_bed": 1,
        }

        first_response = self.client.post(self.placement_create_url, placement_data, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(first_response.data["title"], "Another Hotel by Landlord User")
        self.assertEqual(first_response.data["owner"], self.landlord_user.id)
        self.assertEqual(first_response.data["category"], self.hotel_category.id)
        self.assertEqual(Placement.all_objects.count(), 3)
        self.assertEqual(PlacementDetails.objects.count(), 3)
        self.assertEqual(PlacementLocation.objects.count(), 3)
        self.assertEqual(PlacementLocation.objects.last().placement,
                         Placement.all_objects.get(id=first_response.data["id"]))
        self.assertEqual(PlacementDetails.objects.last().placement,
                         Placement.all_objects.get(id=first_response.data["id"]))

        """
        Sends second POST request with placement details data and expects a 200 OK response.
        Verifies that the placement details is updated correctly.
        """

        placement_details_data = {
            "pets": False,
            "free_wifi": False,
            "smoking": True,
            "parking": True,
            "room_service": False,
            "front_desk_allowed_24": True,
            "free_cancellation": False,
            "balcony": False,
            "air_conditioning": False,
            "washing_machine": False,
            "kitchenette": False,
            "tv": False,
            "coffee_tee_maker": False,
        }

        second_response = self.client.put(self.placement_details_create_url(first_response.data["id"]),
                                          placement_details_data, format="json")

        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertFalse(second_response.data["pets"])
        self.assertTrue(second_response.data["smoking"])
        self.assertTrue(second_response.data["parking"])
        self.assertTrue(second_response.data["front_desk_allowed_24"])

        """
        Sends third POST request with placement images and activation True and expects a 201 CREATED response.
        Verifies that the placement images count increases and has correct link to placement.
        """

        placement_images_data = {
            "activate": True,
            "uploaded_images": [image for image in self.temp_images_set1]
        }

        third_response = self.client.post(self.placement_images_create_url(first_response.data["id"]),
                                          placement_images_data, format="multipart")

        self.assertEqual(third_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(third_response.data["uploaded_images"]), 15)
        self.assertEqual(third_response.data["activate"], "Announcement successfully activated.")
        self.assertTrue(Placement.objects.get(pk=first_response.data["id"]).is_active)
        self.assertEqual(PlacementImage.objects.count(), 31)
        self.assertEqual(PlacementImage.objects.filter(placement=first_response.data["id"]).count(), 15)

    def test_landlord_user_can_create_new_placement_and_cannot_add_more_then_fifteen_images(self):
        """
        Test if landlord user can create new Placement and cannot add more than 15 images and activate Placement.
        Sends first POST request with placement and placement location data and expects a 201 CREATED response.
        """

        placement_data = {
            "placement_location": {
                "country": "Germany",
                "city": "Berlin",
                "post_code": "34567",
                "street": "Test street",
                "house_number": "4"
            },
            "category": self.hotel_category.id,
            "title": "Another Hotel by Landlord User",
            "description": "A" * 60,
            "price": 123,
            "number_of_rooms": 2,
            "placement_area": 40,
            "total_beds": 2,
            "single_bed": 1,
            "double_bed": 1,
        }

        first_response = self.client.post(self.placement_create_url, placement_data, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Placement.all_objects.count(), 3)

        """
        Sends second POST request with placement details data and expects a 200 OK response.
        Verifies that the placement details is updated correctly.
        """

        placement_details_data = {
            "pets": False,
            "free_wifi": False,
            "smoking": True,
            "parking": True,
            "room_service": False,
            "front_desk_allowed_24": True,
            "free_cancellation": False,
            "balcony": False,
            "air_conditioning": False,
            "washing_machine": False,
            "kitchenette": False,
            "tv": False,
            "coffee_tee_maker": False,
        }

        second_response = self.client.put(self.placement_details_create_url(first_response.data["id"]),
                                          placement_details_data, format="json")

        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertFalse(second_response.data["pets"])
        self.assertTrue(second_response.data["smoking"])
        self.assertTrue(second_response.data["parking"])
        self.assertTrue(second_response.data["front_desk_allowed_24"])

        """
        Sends third POST request with too many placement images and activation True 
        and expects a 400 BAD REQUEST response.
        Verifies that the placement images count has not increased and placement wasn't activated.
        """

        placement_images_data = {
            "activate": True,
            "uploaded_images": [image for image in self.temp_images_set2]
        }

        third_response = self.client.post(self.placement_images_create_url(first_response.data["id"]),
                                          placement_images_data, format="multipart")

        self.assertEqual(third_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(third_response.data["uploaded_images"][0], "The maximum number of images cannot exceed 15.")
        self.assertEqual(PlacementImage.objects.count(), 16)
        self.assertFalse(Placement.all_objects.get(pk=first_response.data["id"]).is_active)
        self.assertFalse(Placement.objects.filter(pk=first_response.data["id"]))

    def test_landlord_user_can_create_new_placement_and_cannot_activate_new_placement_without_images(self):
        """
        Test if landlord user can create new Placement and cannot and activate it without uploading images.
        Sends first POST request with placement and placement location data and expects a 201 CREATED response.
        """

        placement_data = {
            "placement_location": {
                "country": "Germany",
                "city": "Berlin",
                "post_code": "34567",
                "street": "Test street",
                "house_number": "4"
            },
            "category": self.hotel_category.id,
            "title": "Another Hotel by Landlord User",
            "description": "A" * 60,
            "price": 123,
            "number_of_rooms": 2,
            "placement_area": 40,
            "total_beds": 2,
            "single_bed": 1,
            "double_bed": 1,
        }

        first_response = self.client.post(self.placement_create_url, placement_data, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Placement.all_objects.count(), 3)

        """
        Sends second POST request with placement details data and expects a 200 OK response.
        Verifies that the placement details is updated correctly.
        """

        placement_details_data = {
            "pets": False,
            "free_wifi": False,
            "smoking": True,
            "parking": True,
            "room_service": False,
            "front_desk_allowed_24": True,
            "free_cancellation": False,
            "balcony": False,
            "air_conditioning": False,
            "washing_machine": False,
            "kitchenette": False,
            "tv": False,
            "coffee_tee_maker": False,
        }

        second_response = self.client.put(self.placement_details_create_url(first_response.data["id"]),
                                          placement_details_data, format="json")

        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertFalse(second_response.data["pets"])
        self.assertTrue(second_response.data["smoking"])
        self.assertTrue(second_response.data["parking"])
        self.assertTrue(second_response.data["front_desk_allowed_24"])

        """
        Sends third POST request without images with activation True and expects a 400 BAD REQUEST response.
        Verifies that the placement images count has not increased and placement wasn't activated.
        """

        placement_images_data = {
            "activate": True,
            "uploaded_images": []
        }

        third_response = self.client.post(self.placement_images_create_url(first_response.data["id"]),
                                          placement_images_data, format="multipart")

        self.assertEqual(third_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(third_response.data["uploaded_images"][0], "This field is required.")
        self.assertFalse(Placement.all_objects.get(pk=first_response.data["id"]).is_active)
        self.assertFalse(Placement.objects.filter(pk=first_response.data["id"]))

    def test_landlord_user_can_create_new_placement_and_cannot_activate_without_details(self):
        """
        Test if landlord user can create new Placement and cannot activate it without filling in the details.
        Sends first POST request with placement and placement location data and expects a 201 CREATED response.
        """

        placement_data = {
            "placement_location": {
                "country": "Germany",
                "city": "Berlin",
                "post_code": "34567",
                "street": "Test street",
                "house_number": "4"
            },
            "category": self.hotel_category.id,
            "title": "Another Hotel by Landlord User",
            "description": "A" * 60,
            "price": 123,
            "number_of_rooms": 2,
            "placement_area": 40,
            "total_beds": 2,
            "single_bed": 1,
            "double_bed": 1,
        }

        first_response = self.client.post(self.placement_create_url, placement_data, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Placement.all_objects.count(), 3)

        """
        Sends second POST request without placement details data and expects a 200 OK response.
        Verifies that the placement details is updated correctly.
        """

        placement_details_data = {
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

        second_response = self.client.put(self.placement_details_create_url(first_response.data["id"]),
                                          placement_details_data, format="json")

        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertFalse(second_response.data["pets"])
        self.assertFalse(second_response.data["smoking"])
        self.assertFalse(second_response.data["parking"])
        self.assertFalse(second_response.data["front_desk_allowed_24"])

        """
        Sends third POST request with placement images and activation True and expects a 201 CREATED response
        and correct "activate" message.
        Verifies that the placement images count increases and has correct link to placement.
        """

        placement_images_data = {
            "activate": True,
            "uploaded_images": [image for image in self.temp_images_set1]
        }

        third_response = self.client.post(self.placement_images_create_url(first_response.data["id"]),
                                          placement_images_data, format="multipart")

        self.assertEqual(third_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(third_response.data["uploaded_images"]), 15)
        self.assertEqual(third_response.data["activate"], "You need to fill in the placement details or add photos.")
        self.assertFalse(Placement.all_objects.get(pk=first_response.data["id"]).is_active)
        self.assertFalse(Placement.objects.filter(pk=first_response.data["id"]))
        self.assertEqual(PlacementImage.objects.count(), 31)
        self.assertEqual(PlacementImage.objects.filter(placement=first_response.data["id"]).count(), 15)

    def test_landlord_user_cannot_create_new_placement_without_category(self):
        """
        Test if landlord user cannot create new Placement without category field.
        Sends a POST request with empty category field and expects a 400 BAD REQUEST response.
        Verifies that the number of placement, placement location, placement details has not increased.
        """

        placement_data = {
            "placement_location": {
                "country": "Germany",
                "city": "Berlin",
                "post_code": "34567",
                "street": "Test street",
                "house_number": "4"
            },
            "category": "",
            "title": "Another Hotel by Landlord User",
            "description": "A" * 60,
            "price": 123,
            "number_of_rooms": 2,
            "placement_area": 40,
            "total_beds": 2,
            "single_bed": 1,
            "double_bed": 1,
        }

        response = self.client.post(self.placement_create_url, placement_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["category"][0], "This field may not be null.")
        self.assertEqual(Placement.all_objects.count(), 2)
        self.assertEqual(PlacementLocation.objects.count(), 2)
        self.assertEqual(PlacementDetails.objects.count(), 2)

    def test_landlord_user_cannot_create_new_placement_without_location_field(self):
        """
        Test if landlord user cannot create new Placement without Location field.
        Sends a POST request without placement location data and expects a 400 BAD REQUEST response.
        Verifies that the number of placement, placement location, placement details has not increased.
        """

        placement_data = {
            "category": self.hotel_category.id,
            "title": "Another Hotel by Landlord User",
            "description": "A" * 60,
            "price": 123,
            "number_of_rooms": 2,
            "placement_area": 40,
            "total_beds": 2,
            "single_bed": 1,
            "double_bed": 1,
        }

        response = self.client.post(self.placement_create_url, placement_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["placement_location"][0], "This field is required.")
        self.assertEqual(Placement.all_objects.count(), 2)
        self.assertEqual(PlacementLocation.objects.count(), 2)
        self.assertEqual(PlacementDetails.objects.count(), 2)

    def test_landlord_user_cannot_create_new_placement_with_empty_location_fields(self):
        """
        Test if landlord user cannot create new Placement with empty Location fields.
        Sends a POST request with empty placement location data and expects a 400 BAD REQUEST response.
        Verifies that the number of placement, placement location, placement details has not increased.
        """

        placement_data = {
            "placement_location": {
                "country": "",
                "city": "",
                "post_code": "",
                "street": "",
                "house_number": ""
            },
            "category": self.hotel_category.id,
            "title": "Another Hotel by Landlord User",
            "description": "A" * 60,
            "price": 123,
            "number_of_rooms": 2,
            "placement_area": 40,
            "total_beds": 2,
            "single_bed": 1,
            "double_bed": 1,
        }

        response = self.client.post(self.placement_create_url, placement_data, format="json")
        response_message = str(response.data["placement_location"])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("country", response_message)
        self.assertIn("city", response_message)
        self.assertIn("post_code", response_message)
        self.assertIn("street", response_message)
        self.assertIn("house_number", response_message)
        self.assertEqual(Placement.all_objects.count(), 2)
        self.assertEqual(PlacementLocation.objects.count(), 2)
        self.assertEqual(PlacementDetails.objects.count(), 2)

    def test_landlord_user_cannot_create_new_placement_with_too_long_fields_length(self):
        """
        Test if landlord user cannot create new Placement with too long length of title, description, country, city,
        post_code, street, house_number fields.
        Sends a POST request with too long length of fields and expects a 400 BAD REQUEST response.
        Verifies that the number of placement, placement location, placement details has not increased.
        """

        placement_data = {
            "placement_location": {
                "country": "A" * 156,
                "city": "A" * 156,
                "post_code": "5" * 6,
                "street": "A" * 156,
                "house_number": "A" * 31
            },
            "category": self.hotel_category.id,
            "title": "A" * 256,
            "description": "A" * 2001,
            "price": 123,
            "number_of_rooms": 2,
            "placement_area": 40,
            "total_beds": 2,
            "single_bed": 1,
            "double_bed": 1,
        }

        response = self.client.post(self.placement_create_url, placement_data, format="json")
        response_message = str(response.data["placement_location"])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("country", response_message)
        self.assertIn("city", response_message)
        self.assertIn("post_code", response_message)
        self.assertIn("street", response_message)
        self.assertIn("house_number", response_message)
        self.assertIn("title", response.data)
        self.assertIn("description", response.data)
        self.assertEqual(Placement.all_objects.count(), 2)
        self.assertEqual(PlacementLocation.objects.count(), 2)
        self.assertEqual(PlacementDetails.objects.count(), 2)

    def test_landlord_user_cannot_create_new_placement_with_too_short_fields_length(self):
        """
        Test if landlord user cannot create new Placement with too short length of description, post_code, fields.
        Sends a POST request with too short length of fields and expects a 400 BAD REQUEST response.
        Verifies that the number of placement, placement location, placement details has not increased.
        """

        placement_data = {
            "placement_location": {
                "country": "Germany",
                "city": "Berlin",
                "post_code": "3456",
                "street": "Test street",
                "house_number": "4"
            },
            "category": self.hotel_category.id,
            "title": "Another Hotel by Landlord User",
            "description": "A" * 39,
            "price": 123,
            "number_of_rooms": 2,
            "placement_area": 40,
            "total_beds": 2,
            "single_bed": 1,
            "double_bed": 1,
        }

        response = self.client.post(self.placement_create_url, placement_data, format="json")
        response_message = str(response.data["placement_location"])

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("post_code", response_message)
        self.assertIn("description", response.data)
        self.assertEqual(Placement.all_objects.count(), 2)
        self.assertEqual(PlacementLocation.objects.count(), 2)
        self.assertEqual(PlacementDetails.objects.count(), 2)

    def test_landlord_user_cannot_create_new_placement_with_too_height_fields_value(self):
        """
        Test if landlord user cannot create new Placement with too height value of price, number_of_rooms,
        placement_area, total_beds, single_bed, double_bed, fields.
        Sends a POST request with too height value of fields and expects a 400 BAD REQUEST response.
        Verifies that the number of placement, placement location, placement details has not increased.
        """

        placement_data = {
            "placement_location": {
                "country": "Germany",
                "city": "Berlin",
                "post_code": "34567",
                "street": "Test street",
                "house_number": "4"
            },
            "category": self.hotel_category.id,
            "title": "Another Hotel by Landlord User",
            "description": "A" * 60,
            "price": 100000,
            "number_of_rooms": 7,
            "placement_area": 500.01,
            "total_beds": 16,
            "single_bed": 16,
            "double_bed": 16,
        }

        response = self.client.post(self.placement_create_url, placement_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)
        self.assertIn("number_of_rooms", response.data)
        self.assertIn("placement_area", response.data)
        self.assertIn("total_beds", response.data)
        self.assertIn("single_bed", response.data)
        self.assertIn("double_bed", response.data)
        self.assertEqual(Placement.all_objects.count(), 2)
        self.assertEqual(PlacementLocation.objects.count(), 2)
        self.assertEqual(PlacementDetails.objects.count(), 2)

    def test_landlord_user_cannot_create_new_placement_with_too_low_fields_value(self):
        """
        Test if landlord user cannot create new Placement with too low value of price, total_beds,
        placement_area, number_of_beds, fields.
        Sends a POST request with too low value of fields and expects a 400 BAD REQUEST response.
        Verifies that the number of placement, placement location, placement details has not increased.
        """

        placement_data = {
            "placement_location": {
                "country": "Germany",
                "city": "Berlin",
                "post_code": "34567",
                "street": "Test street",
                "house_number": "4"
            },
            "category": self.hotel_category.id,
            "title": "Another Hotel by Landlord User",
            "description": "A" * 60,
            "price": 9.99,
            "number_of_rooms": 0,
            "placement_area": 14.99,
            "total_beds": 0,
            "single_bed": 1,
            "double_bed": 1,
        }

        response = self.client.post(self.placement_create_url, placement_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)
        self.assertIn("total_beds", response.data)
        self.assertIn("placement_area", response.data)
        self.assertIn("total_beds", response.data)
        self.assertEqual(Placement.all_objects.count(), 2)
        self.assertEqual(PlacementLocation.objects.count(), 2)
        self.assertEqual(PlacementDetails.objects.count(), 2)

    def test_landlord_user_cannot_create_new_placement_with_zero_beds_fields(self):
        """
        Test if landlord user cannot create new Placement with both zero value of single_bed and double_bed fields.
        Sends a POST request with both empty fields and expects a 400 BAD REQUEST response.
        Verifies that the number of placement, placement location, placement details has not increased.
        """

        placement_data = {
            "placement_location": {
                "country": "Germany",
                "city": "Berlin",
                "post_code": "34567",
                "street": "Test street",
                "house_number": "4"
            },
            "category": self.hotel_category.id,
            "title": "Another Hotel by Landlord User",
            "description": "A" * 60,
            "price": 123,
            "number_of_rooms": 2,
            "placement_area": 40,
            "total_beds": 2,
            "single_bed": 0,
            "double_bed": 0,
        }

        response = self.client.post(self.placement_create_url, placement_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0], "Both bed fields can't be zero.")
        self.assertEqual(Placement.all_objects.count(), 2)
        self.assertEqual(PlacementLocation.objects.count(), 2)
        self.assertEqual(PlacementDetails.objects.count(), 2)

    def test_placement_both_bed_fields_cannot_exceed_total_beds(self):
        """
        Test if landlord user cannot create new Placement with exceeded value of bed fields.
        Sends a POST request with an amount bed values exceeding the total and expects a 400 BAD REQUEST response.
        Verifies that the number of placement, placement location, placement details has not increased.
        """

        placement_data = {
            "placement_location": {
                "country": "Germany",
                "city": "Berlin",
                "post_code": "34567",
                "street": "Test street",
                "house_number": "4"
            },
            "category": self.hotel_category.id,
            "title": "Another Hotel by Landlord User",
            "description": "A" * 60,
            "price": 123,
            "number_of_rooms": 2,
            "placement_area": 40,
            "total_beds": 5,
            "single_bed": 5,
            "double_bed": 1,
        }

        response = self.client.post(self.placement_create_url, placement_data, format="json")

        self.assertEqual(response.data["non_field_errors"][0], "Both bed fields must be equal to the total beds.")
        self.assertEqual(Placement.all_objects.count(), 2)
        self.assertEqual(PlacementLocation.objects.count(), 2)
        self.assertEqual(PlacementDetails.objects.count(), 2)

    def test_placement_both_bed_fields_cannot_be_less_than_total_beds(self):
        """
        Test if landlord user cannot create new Placement with value that is less then of bed fields.
        Sends a POST request with an amount bed values less than the total and expects a 400 BAD REQUEST response.
        Verifies that the number of placement, placement location, placement details has not increased.
        """

        placement_data = {
            "placement_location": {
                "country": "Germany",
                "city": "Berlin",
                "post_code": "34567",
                "street": "Test street",
                "house_number": "4"
            },
            "category": self.hotel_category.id,
            "title": "Another Hotel by Landlord User",
            "description": "A" * 60,
            "price": 123,
            "number_of_rooms": 2,
            "placement_area": 40,
            "total_beds": 5,
            "single_bed": 2,
            "double_bed": 1,
        }

        response = self.client.post(self.placement_create_url, placement_data, format="json")

        self.assertEqual(response.data["non_field_errors"][0], "Both bed fields must be equal to the total beds.")
        self.assertEqual(Placement.all_objects.count(), 2)
        self.assertEqual(PlacementLocation.objects.count(), 2)
        self.assertEqual(PlacementDetails.objects.count(), 2)

    def test_not_landlord_user_cannot_create_new_placement(self):
        """
        Test if not landlord user cannot create new Placement.
        Sends POST request with placement and placement location data and expects a 403 FORBIDDEN response.
        Verifies that the number of placement, placement location, placement details has not increased.
        """

        placement_data = {
            "placement_location": {
                "country": "Germany",
                "city": "Berlin",
                "post_code": "34567",
                "street": "Test street",
                "house_number": "4"
            },
            "category": self.hotel_category.id,
            "title": "Another Hotel by Landlord User",
            "description": "A" * 60,
            "price": 123,
            "number_of_rooms": 2,
            "placement_area": 40,
            "total_beds": 2,
            "single_bed": 1,
            "double_bed": 1,
        }

        refresh = RefreshToken.for_user(self.regular_user)

        self.client.cookies["access_token"] = str(refresh.access_token)
        self.client.cookies["refresh_token"] = str(refresh)

        response = self.client.post(self.placement_create_url, placement_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["detail"], "You do not have permission to perform this action.")
        self.assertEqual(Placement.all_objects.count(), 2)
        self.assertEqual(PlacementLocation.objects.count(), 2)
        self.assertEqual(PlacementDetails.objects.count(), 2)

    def test_unauthorized_user_cannot_create_new_placement(self):
        """
        Test if the unauthorized user cannot create new Placement.
        Send a POST Request with placement and placement location data and expects a 401 UNAUTHORIZED response.
        Verifies that the number of placement, placement location, placement details has not increased.
        """

        placement_data = {
            "placement_location": {
                "country": "Germany",
                "city": "Berlin",
                "post_code": "34567",
                "street": "Test street",
                "house_number": "4"
            },
            "category": self.hotel_category.id,
            "title": "Another Hotel by Landlord User",
            "description": "A" * 60,
            "price": 123,
            "number_of_rooms": 2,
            "placement_area": 40,
            "total_beds": 2,
            "single_bed": 1,
            "double_bed": 1,
        }

        self.client.cookies.clear()

        response = self.client.post(self.placement_create_url, placement_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["detail"], "Authentication credentials were not provided.")
        self.assertEqual(Placement.all_objects.count(), 2)
        self.assertEqual(PlacementLocation.objects.count(), 2)
        self.assertEqual(PlacementDetails.objects.count(), 2)
