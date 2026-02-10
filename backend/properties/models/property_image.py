from typing import Dict

import uuid

from io import BytesIO

from PIL import Image as PILImage
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.utils.translation import gettext_lazy as _


class PropertyImage(models.Model):
    def upload_to(self, filename) -> str:
        ext: str = filename.split('.')[-1]
        new_filename: str = f'{self.property_ref.pk}{uuid.uuid4().hex}.{ext}'
        return f'images/{self.property_ref.property_type.lower()}/{new_filename}'

    property_ref = models.ForeignKey('Property', on_delete=models.CASCADE, related_name='property_images',
                                     verbose_name=_('Property'))
    image = models.ImageField(upload_to=upload_to, verbose_name=_('Image'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    objects = models.Manager()

    def __str__(self) -> str:
        return f'Image to property: {self.property_ref}, id={self.pk}.'

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Property Image')
        verbose_name_plural = _('Property Images')

    @staticmethod
    def _compress_image(image) -> InMemoryUploadedFile:
        img: PILImage.Image = PILImage.open(image)

        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        output: BytesIO = BytesIO()

        format_map: Dict[str, str] = {
            'jpg': 'JPEG',
            'jpeg': 'JPEG',
            'png': 'PNG',
            'gif': 'GIF',
        }

        ext: str = image.name.split('.')[-1].lower()

        img_format: str = format_map.get(ext, 'JPEG')

        try:
            img.save(output, format=img_format, quality=85, optimize=True)
        except OSError:
            output = BytesIO()
            img.save(output, format=img_format, quality=85)

        output.seek(0)

        return InMemoryUploadedFile(output, None, image.name, f'image/{ext}', output.tell(), None)

    def save(self, *args, **kwargs) -> None:
        self.image = self._compress_image(self.image)
        super().save(*args, **kwargs)
