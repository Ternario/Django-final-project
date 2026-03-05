from datetime import datetime
from typing import List

from django.db import transaction
from django.db.models import QuerySet
from more_itertools import chunked

from properties.models import Discount, DiscountProperty, DiscountUser
from properties.services.discount.utils import DISCOUNTS_BATCH_SIZE
from properties.utils.choices.discount import DiscountStatus, DiscountPropertyStatus, DiscountUserStatus
from properties.utils.decorators import atomic_handel
from properties.tasks.service import apply_discounts_task


class CheckDiscountStatus:
    """
    Service class for managing Discount, DiscountProperty and DiscountUser statuses based on datetime.

    This class implements logic to:
        - Expire active discounts whose `valid_until` has passed.
        - Activate scheduled discounts whose `valid_from` has arrived.
        - Expire or activate related DiscountProperty and related DiscountUser entries accordingly.
        - Trigger recalculation of property prices via `apply_discounts_task`.

    Designed for use in:
        - periodic discount status checks,
        - automated recalculation of property prices after discount changes.
    """

    @atomic_handel
    def check_expire(self, date_time: datetime) -> None:
        """
        Expire all active discounts, related DiscountProperty and related DiscountUser entries whose
        `valid_until` has passed.

        Steps:
            - Select all active discounts with `valid_until <= date_time`.
            - Select all active DiscountProperty entries linked to those discounts.
            - Select all active DiscountUser entries linked to those discounts.
            - Bulk update discounts, DiscountProperty and DiscountUser statuses to EXPIRED.
            - Schedule recalculation task for affected properties via Celery.

        Args:
            date_time (datetime): Reference datetime for activation.
        """
        expired_discounts: QuerySet[Discount] = Discount.objects.filter(
            status=DiscountStatus.ACTIVE.value[0], valid_until__lte=date_time
        )

        expired_dp: QuerySet[DiscountProperty] = DiscountProperty.objects.filter(
            discount__in=expired_discounts, status=DiscountPropertyStatus.ACTIVE.value[0]
        )

        expired_du: QuerySet[DiscountUser] = DiscountUser.objects.filter(
            discount__in=expired_discounts, status=DiscountUserStatus.ACTIVE.value[0]
        )

        expired_dp_ids: List[int] = list(expired_dp.values_list('id', flat=True))

        expired_discounts.update(status=DiscountStatus.EXPIRED.value[0], updated_at=date_time)

        expired_dp.update(status=DiscountPropertyStatus.EXPIRED.value[0], updated_at=date_time)
        expired_du.update(status=DiscountUserStatus.EXPIRED.value[0], updated_at=date_time)

        if expired_dp_ids:
            for chunk in chunked(expired_dp_ids, DISCOUNTS_BATCH_SIZE):
                transaction.on_commit(lambda ids=tuple(chunk): apply_discounts_task.delay(list(ids)))

    @atomic_handel
    def check_activation(self, date_time: datetime) -> None:
        """
        Activate all scheduled discounts, related DiscountProperty and related DiscountUser entries whose
        `valid_from` has arrived.

        Steps:
            - Select all scheduled discounts with `valid_from <= date_time`.
            - Select all scheduled DiscountProperty entries linked to those discounts.
            - Bulk update discounts, DiscountProperty and DiscountUser statuses to ACTIVE.
            - Schedule recalculation task for affected properties via Celery.

        Args:
            date_time (datetime): Reference datetime for activation.
        """
        discount_to_activate: QuerySet[Discount] = Discount.objects.filter(
            status=DiscountStatus.SCHEDULED.value[0], valid_from__lte=date_time
        )

        dp_to_activate: QuerySet[DiscountProperty] = DiscountProperty.objects.filter(
            discount__in=discount_to_activate, status=DiscountPropertyStatus.SCHEDULED.value[0]
        )

        du_to_activate: QuerySet[DiscountUser] = DiscountUser.objects.filter(
            discount__in=discount_to_activate, status=DiscountUserStatus.SCHEDULED.value[0]
        )

        dp_to_activate_ids: List[int] = list(dp_to_activate.values_list('id', flat=True))

        discount_to_activate.update(status=DiscountStatus.ACTIVE.value[0], updated_at=date_time)

        dp_to_activate.update(status=DiscountPropertyStatus.ACTIVE.value[0], updated_at=date_time)
        du_to_activate.update(status=DiscountUserStatus.ACTIVE.value[0], updated_at=date_time)

        if dp_to_activate_ids:
            for chunk in chunked(dp_to_activate_ids, DISCOUNTS_BATCH_SIZE):
                transaction.on_commit(lambda ids=tuple(chunk): apply_discounts_task.delay(list(ids)))

    @atomic_handel
    def check_user_expire(self, date_time: datetime):
        """
        Expire all active DiscountUser entries whose `expires_at` has passed.

        Steps:
            - Select all active DiscountUser with `expires_at <= date_time`.
            - Bulk update DiscountUser statuses to EXPIRED.
            - Schedule recalculation task for affected properties via Celery.

        Args:
            date_time (datetime): Reference datetime for activation.
        """
        DiscountUser.objects.filter(
            status=DiscountUserStatus.ACTIVE.value[0], expires_at__lte=date_time
        ).update(
            status=DiscountUserStatus.EXPIRED.value[0], updated_at=date_time
        )
