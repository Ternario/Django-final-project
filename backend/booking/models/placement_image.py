import uuid

from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.utils.translation import gettext_lazy as _

from booking.managers.placement import FilterPlacementRelatedManager


class PlacementImage(models.Model):
    objects = FilterPlacementRelatedManager()

    def upload_to(self, filename):
        ext = filename.split('.')[-1]
        filename = f'{uuid.uuid4().hex}.{ext}'
        return 'images/{}/{}'.format(self.placement.category.name.lower(), filename)

    placement = models.ForeignKey('Placement', on_delete=models.CASCADE, related_name='placement_images',
                                  verbose_name=_('Placement'))
    image = models.ImageField(upload_to=upload_to, blank=False, verbose_name=_('Placement image'))
    created_at = models.DateField(auto_now_add=True, verbose_name=_('Created at'))

    def __str__(self):
        return self.placement

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Placement Image')
        verbose_name_plural = _('Placement Images')

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
