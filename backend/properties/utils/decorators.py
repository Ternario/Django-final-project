import logging
from functools import wraps
from django.db import transaction, DatabaseError

logger = logging.getLogger(__name__)


def atomic_handel(func):
    """
    Decorator that ensures the wrapped function executes within a database transaction.

    - If the function is called within an existing transaction (`atomic` block),
      it executes inside the current transaction.
    - If no transaction is active, it automatically starts a new atomic block.

    Args:
        func (Callable): The function to execute within a database transaction.

    Returns:
        Callable: A wrapped function that is always executed within a safe transaction.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if transaction.get_connection().in_atomic_block:
            return func(*args, **kwargs)

        with transaction.atomic():
            return func(*args, **kwargs)

    return wrapper


def db_errors(func):
    """
    Decorator to catch database-related and unexpected exceptions during function execution.

    Wraps a function and re-raises:
        - DatabaseError with a descriptive message if a Django database error occurs.
        - RuntimeError for any other unexpected exceptions.

    Args:
        func (Callable): The function to wrap.

    Returns:
        Callable: A wrapped version of `func` that consistently handles exceptions.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DatabaseError as e:
            raise DatabaseError(f'Database error in {func.__name__}: {e}') from e
        except Exception as e:
            raise RuntimeError(f'Unexpected error in {func.__name__}: {e}') from e

    return wrapper


def key_error(func):
    """
    Decorator for handling KeyError and general exceptions in email handler methods.

    Designed to be used on instance methods of BaseEmailResponse subclasses.
    Provides centralized logging for:
        - KeyError: Logs the unknown model type via `self.target_model_name`.
        - Exception: Logs unexpected errors along with the user who initiated the action (`self.deleted_by`).

    The decorated method must have `self.target_model_name` and `self.deleted_by` attributes.

    Args:
        func (Callable): The instance method to wrap.

    Returns:
        Callable: A wrapped method that logs exceptions while preserving the original functionality.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except KeyError:
            logger.exception(f'Unknown model type: {self.target_model_name}')
        except Exception as e:
            logger.exception(f'Failed to send delete email for user {self.deleted_by}: {e}')

    return wrapper
