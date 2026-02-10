from enum import Enum

from properties.utils.choices.enumMixin import ChoicesEnumMixin


class ReviewStatus(ChoicesEnumMixin, Enum):
    """
    Statuses of a user review or comment.

    - PUBLISHED: Review is visible publicly.
    - REJECTED: Review was rejected during moderation.
    - DELETED: Review was deleted by the user or admin.
    - PRIVACY_REMOVED: Review anonymized for GDPR or privacy reasons.
    """

    PUBLISHED = ('PUBLISHED', 'Published')
    REJECTED = ('REJECTED', 'Rejected')
    DELETED = ('DELETED', 'Deleted')
    PRIVACY_REMOVED = ('PRIVACY_REMOVED', 'Privacy removed')
