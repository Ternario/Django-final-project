from __future__ import annotations
from typing import TYPE_CHECKING, List, Union

if TYPE_CHECKING:
    from properties.models import User, DeletionLog, LandlordProfile, Property, CompanyMembership, Review

from properties.services.delete.log_model.base import BaseLogModel
from properties.utils.decorators import db_errors
from properties.utils.choices.landlord_profile import LandlordType

DeletableModel = Union[Property, CompanyMembership, Review]


class SoftLogModel(BaseLogModel):
    """
    A utility class to handle deletion logging and anonymization of personal data
    for various models such as User, Property, Review, Company, etc.

    This class supports both single-model deletion and cascade deletions
    (e.g., deleting a landlord profile along with their properties and memberships).

    Attributes:
        deleted_by (User): The user performing the deletion.
        deletion_type (str): Type of deletion (soft, cascade, etc.).
    """

    @db_errors
    def landlord_profile(self, model: LandlordProfile, reason: str | None = None,
                         parent_log: DeletionLog | None = None) -> None:
        """
        Perform cascade deletion for a single landlord profile (individual or company).

        Handles associated properties and company memberships, creating logs for each.

        Args:
            model (IndividualLandlord | Company): The landlord profile to delete.
            reason (str | None): Reason for deletion.
            parent_log (DeletionLog | None, optional): Parent log for cascading deletions.
        """

        parent_log: DeletionLog = self._create_log_model(model, reason, parent_log=parent_log)

        properties: List[Property] = Property.objects.not_deleted(owner=model)

        if model.type == LandlordType.COMPANY.value[0]:
            membership: List[CompanyMembership] = model.company_membership.all()

            if membership:
                for member in membership:
                    self.single_model(member, parent_log=parent_log)

        for prop in properties:
            self.single_model(prop, parent_log=parent_log)

        model.soft_delete()

    @db_errors
    def single_model(self, model: DeletableModel, reason: str | None = None,
                     parent_log: DeletionLog | None = None) -> None:
        """
        Soft-delete a single model instance (Property, Review, or CompanyMembership) and create a deletion log.

        If the model is a Review with feedback, anonymizes personal data before deletion.

        Args:
            model (DeletableModel): The model instance to delete.
            reason (str | None): Reason for deletion.
            parent_log (DeletionLog | None, optional): Parent log if part of a cascade deletion.
        """
        self._create_log_model(model, reason, parent_log=parent_log)

        if isinstance(model, Review) and model.feedback:
            feedback = self._check_personal_data(model.author, model.feedback)

            model.soft_delete(feedback)
        else:
            model.soft_delete()
