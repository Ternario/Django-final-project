from __future__ import annotations

from celery import shared_task
from celery.utils.log import get_task_logger

from properties.models import User, LandlordProfile, Property
from properties.services.delete.soft.landlord import LandlordProfileCascadeDelete
from properties.services.delete.soft.property import PropertyDelete
from properties.services.delete.soft.user import UserCascadeDelete

logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
    retry_backoff=True
)
def user_soft_cascade_delete_task(self, user_id: int, deleted_by: int | None = None) -> None:
    try:
        user: User = User.objects.get(id=user_id, is_deleted=False)
        deleted_by: User = User.objects.get(id=deleted_by, is_deleted=False) if deleted_by else user

        reason: str = 'Owner request'

        handler: UserCascadeDelete = UserCascadeDelete.create(target_model=user, deleted_by=deleted_by, reason=reason)
        handler.execute()

    except User.DoesNotExist:
        logger.warning(f'User: {user_id} is already soft deleted or deletion initiator: {deleted_by} not found.')
        return


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
    retry_backoff=True
)
def landlord_soft_cascade_delete_task(self, instance_id: int, deleted_by: int) -> None:
    try:
        lp_instance: LandlordProfile = LandlordProfile.objects.get(id=instance_id)
        user: User = User.objects.get(id=deleted_by)

        reason: str = 'Owner request'
        handler: LandlordProfileCascadeDelete = LandlordProfileCascadeDelete.create(
            target_model=lp_instance, deleted_by=user, reason=reason
        )
        handler.execute()

    except LandlordProfile.DoesNotExist:
        logger.warning(f'Landlord profile: {instance_id} is not found')
        return
    except User.DoesNotExist:
        logger.warning(f'User: {deleted_by} is not found')
        return


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
    retry_backoff=True
)
def property_soft_delete_task(self, instance_id: int, deleted_by_id: int) -> None:
    try:
        prop_instance: Property = Property.objects.get(id=instance_id)
        user: User = User.objects.get(id=deleted_by_id)

        reason: str = 'Owner request'

        handler: PropertyDelete = PropertyDelete.create(
            target_model=prop_instance, deleted_by=user, reason=reason
        )
        handler.execute()

    except Property.DoesNotExist:
        logger.warning(f'Property: {instance_id} is not found')
        return
    except User.DoesNotExist:
        logger.warning(f'User: {deleted_by_id} is not found')
        return
