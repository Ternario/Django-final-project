import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base_config.settings')

app = Celery('properties')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'currency-rate-update-every-hour': {
        'task': 'properties.tasks.periodic.currency_rate_update_tasks',
        'schedule': crontab(minute=0, hour='*')
        #         # 'schedule': crontab(minute='*')
    },
    'check-discount-status-expire-every-hour': {
        'task': 'properties.tasks.periodic.status_checker_expire_tasks',
        'schedule': crontab(minute=1, hour='*')
        # 'schedule': crontab(minute='*/2')
    },
    'check-discount-status-activate-every-hour': {
        'task': 'properties.tasks.periodic.status_checker_activate_tasks',
        'schedule': crontab(minute=2, hour='*')
        #         'schedule': crontab(minute='*/3')
    },
    'check-discount-user-expire-status-every-hour': {
        'task': 'properties.tasks.periodic.status_checker_user_expire_tasks',
        'schedule': crontab(minute=3, hour='*')
        #         'schedule': crontab(minute='*/4')

    }
}
