from __future__ import annotations
from typing import TYPE_CHECKING, List, Union, Set

from django.db import transaction

from properties.tasks.service import update_user_company_member_to_regular_task

if TYPE_CHECKING:
    from properties.models import DeletionLog, LandlordProfile

from properties.models import Property, Review, Booking, CompanyMembership, Discount
from properties.services.delete.log_model.base import BaseLogModel
from properties.utils.decorators import db_errors

from properties.utils.choices.landlord_profile import LandlordType

SingleModels = Union[Review, Booking, CompanyMembership, Discount]


class PrivacyLogModel(BaseLogModel):
    """
    Logging model for privacy (depersonalization) deletions.

    This class extends `BaseLogModel` to provide specific logging functionality
    for privacy-related operations, including depersonalization of users and
    associated models such as reviews, bookings, landlord profiles, properties,
    and company memberships.

    Responsibilities:
        - Create structured logs for each depersonalization or soft deletion.
        - Cascade logging for related entities (e.g., landlord properties, memberships).
        - Handle conditional logic for models that require data sanitization
          (e.g., anonymizing feedback text in reviews).
    """

    @db_errors
    def landlord_profile(self, model: LandlordProfile, parent_log: DeletionLog) -> None:
        """
        Log and depersonalize a landlord profile and its related entities.

        For individual landlords, all associated properties are soft-deleted.
        For companies, both properties and memberships are soft-deleted,
        while the company itself is depersonalized.

        Args:
            model (IndividualLandlord | Company): The landlord profile to depersonalize.
            parent_log (DeletionLog): Parent log entry.
        """
        parent_log: DeletionLog = self._create_log_model(model, parent_log=parent_log)

        properties: List[Property] = list(Property.objects.filter(owner_id=model.pk))

        if model.type == LandlordType.INDIVIDUAL.value[0]:
            booking_list: List[Booking] = Booking.objects.filter(property_ref__owner_id=model.pk)

            if booking_list:
                for booking in booking_list:
                    booking.property_owner_privacy_delete()

        membership: List[CompanyMembership] = list(CompanyMembership.objects.filter(company_id=model.pk))
        membership_ids: List[int] = [cm.user_id for cm in membership]

        users_with_other_companies: Set[int] = set(
            CompanyMembership.objects.filter(
                user_id__in=membership_ids, is_deleted=False
            ).exclude(company_id=model.pk).values_list('user_id', flat=True)
        )

        if membership:
            for member in membership:
                m_id: int = member.user_id

                if m_id not in users_with_other_companies:
                    transaction.on_commit(lambda u_id=m_id: update_user_company_member_to_regular_task.delay(u_id))

                self.single_model_soft(member, parent_log=parent_log)

        for prop in properties:
            self.single_model_soft(prop, parent_log=parent_log)

        model.privacy_delete()

    @db_errors
    def single_model(self, model: SingleModels, parent_log: DeletionLog) -> None:
        """
        Log and depersonalize a single model instance (Review or Booking).

        Reviews are additionally checked for personal data in their feedback field.
        If feedback is present, it is sanitized before depersonalization.

        Args:
            model (Review | Booking): Instance to depersonalize.
            parent_log (DeletionLog): Parent log entry.
        """
        self._create_log_model(model, parent_log=parent_log)

        if isinstance(model, Review) and model.feedback:
            feedback: str = self._check_personal_data(model.author, model.feedback)

            model.privacy_delete(feedback)
            return
        model.privacy_delete()

    @db_errors
    def single_model_soft(self, model: Property | CompanyMembership, parent_log: DeletionLog) -> None:
        """
        Log and soft-delete a model instance (Property or CompanyMembership).

        This method does not fully depersonalize data, but instead marks the
        instance as soft-deleted in the database.

        Args:
            model (Property | CompanyMembership): Instance to soft-delete.
            parent_log (DeletionLog): Parent log entry.
        """
        self._create_log_model(model, parent_log=parent_log)

        model.soft_delete()
