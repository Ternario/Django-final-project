from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from properties.models import User, DeletionLog
    from django.db.models import QuerySet

from django.db import models


class DeletionLogManager(models.Manager):
    """
    Custom manager for DeletionLog model that provides utility methods
    to query deletion logs based on the user who performed the deletion
    or the model that was deleted.

    Supports:
        - Retrieving all deletion logs created by a specific user.
        - Retrieving all deletion logs related to a specific model.

    Methods:
        for_user(user: User) -> QuerySet[DeletionLog]
            Returns all deletion logs created by the specified user.
        for_model(model: models.Model) -> QuerySet[DeletionLog]
            Returns all deletion logs related to the specified model.
    """

    def for_user(self, user: User, **kwargs: Any) -> QuerySet[DeletionLog]:
        """
        Retrieve all deletion logs created by the given user.

        Args:
            user (User): The user who performed the deletion.

        Returns:
            QuerySet[DeletionLog]: QuerySet containing all logs where `deleted_by` matches the user.

        """
        return self.filter(deleted_by=user, **kwargs)

    def for_model(self, model: models.Model, **kwargs: Any) -> QuerySet[DeletionLog]:
        """
        Retrieve all deletion logs for a specific model instance.

        Args:
            model (models.Model): The model instance that was deleted.

        Returns:
            QuerySet[DeletionLog]: QuerySet containing all logs where `deleted_model` matches the provided model.
        """
        return self.filter(deleted_model=model, **kwargs)
