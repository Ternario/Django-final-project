from __future__ import annotations

from typing import List, Dict

# Raw data to create CrontabSchedule and PeriodicTask models
celery_tasks: List[Dict[str, str | int]] = [
    {
        'task': 'properties.tasks.periodic.currency_rate_update_tasks',
        'minute': 30,
        'minute_offset': 0,
        'hour': '*'
    },
    {
        'task': 'properties.tasks.periodic.status_checker_expire_tasks',
        'minute': 30,
        'minute_offset': 1,
        'hour': '*'
    },
    {
        'task': 'properties.tasks.periodic.status_checker_activate_tasks',
        'minute': 30,
        'minute_offset': 2,
        'hour': '*'
    },
    {
        'task': 'properties.tasks.periodic.status_checker_user_expire_tasks',
        'minute': 30,
        'minute_offset': 3,
        'hour': '*'
    }
]


def build_minute_expr(minute_interval: int, minute_offset: int) -> str:
    """
    Returns a cron-compatible minute expression for a given interval and offset.

    Args:
        minute_interval (int): Interval in minutes (e.g., 1, 2, 3, 30, 60).
        minute_offset (int): Offset in minutes (0-59) to start the schedule.

    Returns:
        str: A string suitable for the 'minute' field in CrontabSchedule.
    """
    if minute_interval == 60:
        return str(minute_offset)

    elif minute_interval >= 1:
        return f'{minute_offset}-59/{minute_interval}'
