from datetime import datetime

from django.utils.timezone import now

from properties.models import Discount
from properties.utils.choices.discount import DiscountStatus


class CheckDiscountExpire:
    """
    Updates discount statuses based on the current date and time.

    Provides:
        - Expiration of active discounts whose `valid_until` has passed.
        - Activation of scheduled discounts whose `valid_from` has arrived.
        - Efficient bulk updates via Django ORM `update()` without loading objects into memory.
    """

    @staticmethod
    def check_expire(date_time) -> None:
        """
        Mark all active discounts as EXPIRED if their `valid_until` is less than or equal
        to the given datetime.

        Args:
            date_time (datetime): Reference datetime for expiration.
        """
        Discount.objects.filter(
            status=DiscountStatus.ACTIVE.value[0], valid_until__lte=date_time
        ).update(
            status=DiscountStatus.EXPIRED.value[0], updated_at=date_time
        )

    @staticmethod
    def check_activation(date_time) -> None:
        """
        Mark all scheduled discounts as ACTIVE if their `valid_from` is less than or equal
        to the given datetime.

        Args:
            date_time (datetime): Reference datetime for activation.
        """
        Discount.objects.filter(
            status=DiscountStatus.SCHEDULED.value[0], valid_from__lte=date_time
        ).update(
            status=DiscountStatus.ACTIVE.value[0], updated_at=date_time
        )

    def run(self):
        """
        Execute both expiration and activation checks using the current datetime.
        """
        date_time: datetime = now()

        self.check_expire(date_time)
        self.check_activation(date_time)
