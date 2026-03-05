from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, List

import logging
from django.db.models import Avg, Count, QuerySet

from properties.models import Property, Review
from properties.utils.choices.review import ReviewStatus

logger = logging.getLogger(__name__)


class PropertyRatingUpdater:
    """
    Service class for recalculating and updating Property ratings and review counts.

    This class implements logic to:
        - Fetch all reviews associated with a given Property or list of Properties.
        - Include only reviews with relevant statuses (e.g., published or soft-deleted).
        - Calculate the average rating and total number of reviews per property.
        - Update the Property instance(s) with the calculated rating and review count.
        - Round average ratings to one decimal place using ROUND_HALF_UP.
        - Efficiently handle bulk updates for multiple properties to minimize database queries.

    Designed for use in:
        - Updating Property ratings after new reviews are created.
        - Bulk recalculation tasks when multiple reviews are deleted.
        - Celery tasks or synchronous service calls.
    """

    @staticmethod
    def execute(prop_id: int) -> None:
        """
        Recalculate and update rating and review count for a single Property.

        Steps:
            - Retrieve the Property instance by ID.
            - Aggregate reviews to compute average rating and total count.
            - Update the Property's `rating` and `review_count` fields.
            - Save changes to the database.

        Args:
            prop_id (int): The ID of the Property to update.

        Notes:
            - If the Property does not exist, the operation is skipped with a warning.
            - Average rating is rounded to one decimal place.
            - Review count defaults to 0 if there are no reviews.
        """
        try:
            instance: Property = Property.objects.get(id=prop_id)
        except Property.DoesNotExist:
            logger.warning(f'Property {prop_id} does not exist, skipping rating update.')
            return

        results: Dict[str, Any] = Review.objects.filter(
            property_ref_id=instance.pk,
            status__in=[ReviewStatus.PUBLISHED.value[0], ReviewStatus.SOFT_DELETED.value[0]]
        ).aggregate(
            avg_rating=Avg('rating'),
            review_count=Count('id')
        )

        instance.rating = (Decimal(results['avg_rating'] or 0).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
        instance.review_count = results['review_count'] or 0

        instance.save(update_fields=['rating', 'review_count'])

    @staticmethod
    def execute_list(prop_ids: List[int]) -> None:
        """
        Recalculate and update ratings and review counts for multiple Properties.

        Steps:
            - Fetch all Property instances for the given list of IDs.
            - Aggregate associated reviews grouped by `property_ref_id`.
            - Construct a mapping of Property ID → aggregated rating and count.
            - Update each Property instance with its corresponding values.
            - Use `bulk_update` to efficiently save all changes in a single query.

        Args:
            prop_ids (List[int]): List of Property IDs to update.

        Notes:
            - Properties with no reviews will have `rating` set to 0.0 and `review_count` set to 0.
            - Average rating is rounded to one decimal place using ROUND_HALF_UP.
            - This method minimizes database queries by aggregating reviews for all properties at once.
        """
        properties: QuerySet[Property] = Property.objects.filter(id__in=prop_ids)

        results: List[Dict[str, Any]] = Review.objects.filter(
            property_ref_id__in=prop_ids,
            status__in=[ReviewStatus.PUBLISHED.value[0], ReviewStatus.SOFT_DELETED.value[0]]
        ).values(
            'property_ref_id'
        ).annotate(
            avg_rating=Avg('rating'),
            review_count=Count('id')
        )

        result_map: Dict[int, Dict[str, Any]] = {
            r['property_ref_id']: {
                'avg_rating': r['avg_rating'],
                'review_count': r['review_count']
            }
            for r in results
        }

        for prop in properties:
            new_data: Dict[str, Any] = result_map.get(prop.pk, {'avg_rating': 0, 'review_count': 0})
            prop.rating = (Decimal(new_data['avg_rating'] or 0).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
            prop.review_count = new_data['review_count'] or 0

        Property.objects.bulk_update(properties, ['rating', 'review_count'])
