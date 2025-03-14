from datetime import datetime

from django.db import models

from booking_project.models import Placement
from booking_project.utils.placement_manager import FilterPlacementRelatedManager


class PlacementImage(models.Model):
    objects = FilterPlacementRelatedManager()

    def upload_to(self, filename):
        filename, ext = filename.split('.')
        time = str(datetime.now().strftime('%d_%m_%Y_%H_%M_%S'))
        filename = f"{filename}_{time}.{ext}"
        return '{}/{}/{}'.format(self.placement.owner.id, self.placement.id, filename)

    placement = models.ForeignKey(Placement, on_delete=models.CASCADE, related_name='placement_image')
    image = models.ImageField(upload_to=upload_to, blank=False, verbose_name='Placement image')
