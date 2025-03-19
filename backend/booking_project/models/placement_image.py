import uuid

from datetime import datetime
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models

from booking_project.models import Placement
from booking_project.utils.placement_manager import FilterPlacementRelatedManager


class PlacementImage(models.Model):
    objects = FilterPlacementRelatedManager()

    def upload_to(self, filename):
        ext = filename.split('.')[-1]
        filename = f'{uuid.uuid4().hex}.{ext}'
        return 'images/{}/{}'.format(self.placement.category.name.lower(), filename)

    placement = models.ForeignKey(Placement, on_delete=models.CASCADE, related_name='placement_image')
    image = models.ImageField(upload_to=upload_to, blank=False, verbose_name='Placement image')

    def __str__(self):
        return self.placement

    def compress_image(self, image):
        img = Image.open(image)

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        output = BytesIO()

        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)

        return InMemoryUploadedFile(output, None, image.name, 'image/jpeg', output.tell(), None)

    def save(self, *args, **kwargs):
        if self.image:
            self.image = self.compress_image(self.image)
        super().save(*args, **kwargs)
