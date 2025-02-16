from datetime import datetime

from django.db import models

from booking_project.models import Placement


class PlacementImage(models.Model):
    objects = models.Manager()

    def upload_to(self, filename):
        filename, ext = filename.split('.')
        time = str(datetime.now().strftime("%d_%m_%Y %H_%M_%S"))
        filename = f"{filename}_{time}.{ext}"
        return '{}/{}/{}'.format(self.placement.owner.id, self.placement.id, filename)

    placement = models.ForeignKey(Placement, on_delete=models.CASCADE, related_name='placement_images')
    placement_image = models.ImageField(upload_to=upload_to, blank=True, null=True, verbose_name="Placement images")
