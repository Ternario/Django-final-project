import os
import shutil

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import override_settings

from properties.models import PlacementImage
from properties.tests.models.base_models_setup import BaseModelSetupTest


@override_settings(MEDIA_ROOT=os.path.join(settings.BASE_DIR, "test_media"))
class PlacementImageModelTest(BaseModelSetupTest):
    @classmethod
    def tearDownClass(cls):
        """Deletes the test dir with all files and folders after the tests are completed."""

        if os.path.basename(settings.MEDIA_ROOT) == "test_media":
            shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

        super().tearDownClass()

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.temp_image = SimpleUploadedFile("test_image.jpg",
                                            (
                                                b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00'
                                                b'\x00\xFF\xFF\xFF\x21\xF9\x04\x01\x0A\x00\x00\x00\x2C\x00'
                                                b'\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B'
                                            ),
                                            content_type="image/jpeg")

        cls.placement_image = PlacementImage.objects.create(
            placement=cls.placement,
            image=cls.temp_image
        )

    def test_create_placement_image(self):
        """Test creating a placement image."""

        expected_path = os.path.normpath(self.placement_image.image.name)
        image_path = os.path.normpath(self.placement_image.image.path)

        self.assertIsNotNone(self.placement_image.id)
        self.assertIsNotNone(self.placement_image.placement)
        self.assertTrue(image_path.endswith(expected_path))

    def test_image_cannot_be_created_without_placement(self):
        """Test the image cannot be created without placement or image field."""

        new_image = PlacementImage(
            placement=None,
            image=None
        )

        with self.assertRaises(ValidationError) as context:
            new_image.full_clean()
        error_message = str(context.exception)
        self.assertIn("placement", error_message)
        self.assertIn("image", error_message)
