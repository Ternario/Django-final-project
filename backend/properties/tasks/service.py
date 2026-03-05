from __future__ import annotations

from typing import List

from celery import shared_task
from celery.utils.log import get_task_logger

from properties.models import User

from properties.services.discount.applier import DiscountApplier
from properties.services.property.rating_updater import PropertyRatingUpdater
from properties.utils.choices.landlord_profile import LandlordType

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 5},
    retry_backoff=True
)
def apply_discounts_task(dp_ids: List[int]) -> None:
    DiscountApplier().execute(dp_ids)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
    retry_backoff=True
)
def rating_updater_task(prop_id: int | List[int]) -> None:
    if isinstance(prop_id, list):
        PropertyRatingUpdater.execute_list(prop_id)
    else:
        PropertyRatingUpdater.execute(prop_id)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2},
    retry_backoff=True
)
def update_user_company_member_to_regular_task(u_id: int) -> None:
    try:
        user: User = User.objects.get(id=u_id)
        user.is_landlord = False
        user.landlord_type = LandlordType.NONE.value[0]
        user.save(update_fields=['is_landlord', 'landlord_type', 'updated_at'])

    except User.DoesNotExist:
        logger.warning(f'User: {u_id} is not found')
        return
