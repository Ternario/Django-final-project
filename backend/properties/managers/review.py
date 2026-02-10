from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from properties.models import Review

from django.db import models
from django.db.models import QuerySet

from properties.utils.choices.review import ReviewStatus


class CustomReviewManager(models.Manager):
    """
    Custom manager for the Review model that provides utility methods
    to filter reviews based on their publication status and deletion flag.

    Supports:
        - Retrieving published reviews.
        - Retrieving inactive or rejected reviews.
        - Retrieving deleted reviews.
        - Retrieving all non-deleted reviews.

    Methods:
        published() -> QuerySet[Review]
            Returns all reviews with status PUBLISHED.
        rejected() -> QuerySet[Review]
            Returns all reviews with status REJECTED.
        deleted() -> QuerySet[Review]
            Returns all reviews marked as deleted.
        not_deleted() -> QuerySet[Review]
            Returns all reviews that are not marked as deleted.
    """

    def published(self, **kwargs: Any) -> QuerySet[Review]:
        """
        Retrieve all published reviews.

        Returns:
            QuerySet[Review]: QuerySet containing reviews where `status` is PUBLISHED.
        """
        return self.filter(status=ReviewStatus.PUBLISHED.value[0], **kwargs)

    def rejected(self, **kwargs: Any) -> QuerySet[Review]:
        """
        Retrieve all r rejected reviews.

        Returns:
            QuerySet[Review]: QuerySet containing reviews where `status` is REJECTED.
        """
        return self.filter(status=ReviewStatus.REJECTED.value[0], **kwargs)

    def deleted(self, **kwargs: Any) -> QuerySet[Review]:
        """
        Retrieve all deleted reviews.

        Returns:
            QuerySet[Review]: QuerySet containing reviews where `is_deleted=True`.
        """
        return self.filter(is_deleted=True, **kwargs)

    def not_deleted(self, **kwargs: Any) -> QuerySet[Review]:
        """
        Retrieve all reviews that are not marked as deleted.

        Returns:
            QuerySet[Review]: QuerySet containing reviews where `is_deleted=False`.
        """
        return self.filter(is_deleted=False, **kwargs)
