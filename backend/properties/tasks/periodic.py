from celery import shared_task
from django.utils.timezone import now

from properties.services.currency.rate_checker import CurrencyRateChecker
from properties.services.discount.status_checker import CheckDiscountStatus


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
    retry_backoff=True
)
def currency_rate_update_tasks(self) -> None:
    CurrencyRateChecker.run()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
    retry_backoff=True
)
def status_checker_expire_tasks(self) -> None:
    CheckDiscountStatus().check_expire(now())


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
    retry_backoff=True
)
def status_checker_activate_tasks(self) -> None:
    CheckDiscountStatus().check_activation(now())


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3},
    retry_backoff=True
)
def status_checker_user_expire_tasks(self) -> None:
    CheckDiscountStatus().check_user_expire(now())
