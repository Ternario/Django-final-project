import io
import os
import shutil

from PIL import Image

from django.conf import settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from booking_project.models import Placement, PlacementDetails, PlacementImage, PlacementLocation
from booking_project.tests.api.base_setup_data.users_setup_data import BaseUsersSetupData


def create_fake_image():
    image_io = io.BytesIO()
    img = Image.new('RGB', (100, 100), color='red')
    img.save(image_io, 'JPEG')
    image_io.seek(0)

    return SimpleUploadedFile("fake_image.jpg", image_io.read(), content_type="image/jpeg")


class PlacementSetup(BaseUsersSetupData):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_media = os.path.join(settings.BASE_DIR, 'test_media')
        os.makedirs(cls.test_media, exist_ok=True)
        settings.MEDIA_ROOT = cls.test_media

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(cls.test_media, ignore_errors=True)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.temp_images_set1 = [create_fake_image() for _ in range(15)]
        cls.temp_images_set2 = [create_fake_image() for _ in range(16)]

        cls.add_temp_images_set1 = [create_fake_image() for _ in range(7)]

        cls.placement_active_list_url = reverse("placement-list")

        cls.placement_create_url = reverse("placement-create")
        cls.placement_details_create_url = lambda pk: reverse("placement-create-details", kwargs={"placement": pk})
        cls.placement_images_create_url = lambda pk: reverse("placement-create-images", kwargs={"placement": pk})
        cls.placement_activation = lambda pk: reverse("placement-activation", kwargs={"pk": pk})

        cls.placement_retrieve_update_delete_url = lambda pk: reverse("placement", kwargs={"pk": pk})
        cls.placement_details_retrieve_update_url = lambda pk: reverse("placement-details", kwargs={"placement": pk})
        cls.placement_location_retrieve_update_url = lambda pk: reverse("placement-location", kwargs={"placement": pk})
        cls.placement_image_retrieve_delete_url = lambda pk: reverse("placement-images", kwargs={"placement": pk})

        cls.my_active_placement_list_url = reverse("my-active-list")

        cls.my_inactive_placement_list_url = reverse("my-inactive-list")
        cls.inactive_placement_retrieve_update_delete_url = lambda pk: reverse("inactive-placement-details",
                                                                               kwargs={"pk": pk})

    def setUp(self):
        super().setUp()

        self.placement = Placement.objects.create(
            owner=self.landlord_user,
            category=self.hotel_category,
            title="First Hotel by Landlord User",
            description="A" * 50,
            price=250,
            number_of_rooms=2,
            placement_area=43.5,
            total_beds=3,
            single_bed=2,
            double_bed=1,
            is_active=True
        )

        self.placement_location = PlacementLocation.objects.create(
            placement=self.placement,
            country="Test Country",
            city="Test first city",
            post_code="10405",
            street="Test street",
            house_number="1"
        )

        self.placement_details = PlacementDetails.objects.create(
            placement=self.placement,
            pets=True,
            free_wifi=False,
            smoking=False,
            parking=False,
            room_service=True,
            front_desk_allowed_24=False,
            free_cancellation=False,
            balcony=True,
            air_conditioning=False,
            washing_machine=False,
            kitchenette=False,
            tv=False,
            coffee_tee_maker=True
        )

        self.placement_images = PlacementImage.objects.bulk_create([
            PlacementImage(placement=self.placement, image=create_fake_image()) for _ in range(8)
        ])

        self.inactive_placement = Placement.objects.create(
            owner=self.landlord_user,
            category=self.hostel_category,
            title="First Hostel by Landlord User",
            description="A" * 50,
            price=250,
            number_of_rooms=2,
            placement_area=43.5,
            total_beds=3,
            single_bed=2,
            double_bed=1,
            is_active=False
        )

        self.inactive_placement_location = PlacementLocation.objects.create(
            placement=self.inactive_placement,
            country="Test Country",
            city="Test city",
            post_code="10405",
            street="Test street",
            house_number="1"
        )

        self.inactive_placement_details = PlacementDetails.objects.create(
            placement=self.inactive_placement,
            pets=True,
            free_wifi=False,
            smoking=False,
            parking=False,
            room_service=True,
            front_desk_allowed_24=False,
            free_cancellation=False,
            balcony=True,
            air_conditioning=False,
            washing_machine=False,
            kitchenette=False,
            tv=False,
            coffee_tee_maker=True
        )

        self.inactive_placement_images = PlacementImage.objects.bulk_create([
            PlacementImage(placement=self.inactive_placement, image=create_fake_image()) for _ in range(8)
        ])
