import os
import shutil
from datetime import datetime

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from booking_project.models import PlacementImage
from booking_project.tests.models.placement_setup import PlacementSetupTest


class PlacementImageModelTest(PlacementSetupTest):

    @classmethod
    def setUpClass(cls):
        """Created a separate test dir before running the tests."""
        super().setUpClass()

        cls.test_media = os.path.join(settings.BASE_DIR, 'test_media')
        os.makedirs(cls.test_media, exist_ok=True)
        settings.MEDIA_ROOT = cls.test_media

    @classmethod
    def tearDownClass(cls):
        """Deletes the test dir with all files and folders after the tests are completed."""
        super().tearDownClass()
        shutil.rmtree(cls.test_media, ignore_errors=True)

    def setUp(self):
        super().setUp()

        self.temp_image = SimpleUploadedFile("test_image.jpg",
                                             (
                                                 b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00'
                                                 b'\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x0A\x00\x00\x00\x2C\x00'
                                                 b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B'
                                             ),
                                             content_type="image/jpeg")

        self.time = str(datetime.now().strftime('%d_%m_%Y_%H_%M_%S'))

        self.placement_image = PlacementImage.objects.create(
            placement=self.placement,
            image=self.temp_image
        )

    def test_create_placement_image(self):
        """Test creating a placement image."""

        expected_filename = f"test_image_{self.time}.jpg"
        expected_path = f"{self.placement.owner.id}/{self.placement.id}/{expected_filename}"

        self.assertIsNotNone(self.placement_image.id)
        self.assertIsNotNone(self.placement_image.placement)
        self.assertTrue(self.placement_image.image.path.endswith(expected_filename))
        self.assertEqual(self.placement_image.image.name, expected_path)
