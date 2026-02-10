from __future__ import annotations
from typing import TYPE_CHECKING, List, Union

if TYPE_CHECKING:
    from properties.models import (
        User, DeletionLog, LandlordProfile, Property, CompanyMembership, Review, Booking, Discount
    )

import re

from abc import ABC, abstractmethod

from django.contrib.contenttypes.models import ContentType
from django.db import IntegrityError, DatabaseError, models

from properties.utils.constants.default_depersonalization_values import DELETED_USER_PLACEHOLDER
from properties.utils.decorators import db_errors

DeletableModel = Union[Property, CompanyMembership, Review]


class BaseLogModel(ABC):
    """
    A utility class to handle deletion logging and anonymization of personal data
    for various models such as User, Property, Review, Company, etc.

    This class supports both single-model deletion and cascade deletions
    (e.g., deleting a landlord profile along with their properties and memberships).

    Attributes:
        deleted_by (User): The user performing the deletion.
        deletion_type (str): Type of deletion (soft, cascade, etc.).
    """

    def __init__(self, deleted_by: User, deletion_type: str):
        self.deleted_by = deleted_by
        self.deletion_type = deletion_type

    def _create_log_model(self, model: models.Model, reason: str | None = None,
                          parent_log: DeletionLog | None = None) -> DeletionLog:
        """
        Create and save a DeletionLog entry for a given model instance.

        Args:
            model (models.Model): The model instance being deleted.
            reason (str): Reason for deletion.
            parent_log (DeletionLog | None, optional): Parent deletion log if cascading. Defaults to None.

        Returns:
            DeletionLog: The newly created deletion log instance.

        Raises:
            RuntimeError: If creating the log fails due to database errors.
        """
        try:
            content_type: ContentType = ContentType.objects.get_for_model(model.__class__)

            deletion_log = DeletionLog(
                deleted_by=self.deleted_by,
                deleted_model=content_type,
                deleted_model_name=f'{model._meta.app_label}.{model._meta.model_name}',
                deleted_object_id=model.pk,
                reason=reason,
                deletion_type=self.deletion_type,
                is_cascade=bool(parent_log),
                parent_log=parent_log,
                parent_log_name=parent_log._meta.model_name if parent_log else ''
            )
            deletion_log.save()
            return deletion_log
        except (IntegrityError, DatabaseError) as e:
            raise RuntimeError(
                f'Failed to create deletion log for {model.__class__.__name__} with id={model.pk}') from e

    @staticmethod
    def _split_to_words(value: str) -> set[str]:
        """
        Split a string into a set of lowercase words, removing digits and common separators.

        Splits the input string by characters such as ',', '.', '-', '_', '+', and also removes digits.
        Useful for breaking down emails, usernames, or other identifiers into searchable components.

        Args:
            value (str): The input string to split.

        Returns:
            set[str]: A set of lowercase words extracted from the input string.
        """
        return {
            pure_word.lower()
            for sep_word in re.split(r'[,.\-_+]', value) if sep_word
            for pure_word in re.split(r'[0-9]', sep_word) if pure_word
        }

    def _check_personal_data(self, author: User, feedback: str) -> str:
        """
        Redact personal information of a user from feedback text.

        Replaces occurrences of the user's email, username, first name, and last name
        with a placeholder in the provided feedback text. Handles cases where username is empty.

        Args:
            author (User): The user whose personal data should be redacted.
            feedback (str): The original feedback text containing potential personal data.

        Returns:
            str: The feedback text with personal data replaced by a placeholder.
        """
        author_email: set[str] = self._split_to_words(author.email.split('@')[0])
        author_username: set[str] = self._split_to_words(author.username) if author.username else set()

        personal_data: set[str] = author_email | author_username | {
            author.first_name.lower(),
            author.last_name.lower(),
        }

        cleaned_feedback = feedback

        for data in personal_data:
            pattern = re.compile(re.escape(data), re.IGNORECASE)
            cleaned_feedback = pattern.sub(DELETED_USER_PLACEHOLDER, cleaned_feedback)

        return cleaned_feedback

    @db_errors
    def user_log(self, model: User, reason: str) -> DeletionLog:
        """
        Create a deletion log entry specifically for a User instance.

        Args:
            model (User): The user being deleted.
            reason (str): Reason for deletion.

        Returns:
            DeletionLog: The created deletion log.
        """
        return self._create_log_model(model, reason)

    @db_errors
    def list_handler(self, model_list: List[Review] | List[Booking] | List[Discount] | List[CompanyMembership],
                     parent_log: DeletionLog) -> None:
        """
        Perform cascade deletion for a list of reviews and log each deletion.

        Each review in the provided list is soft-deleted via `single_model`, and a
        corresponding deletion entry is recorded under the given parent log.

        Args:
            model_list (List[Review]): List of Review instances to be deleted.
            parent_log (DeletionLog): Parent deletion log to associate all review deletions with.

        Returns:
            None
        """
        for model in model_list:
            self.single_model(model, parent_log=parent_log)

    @db_errors
    def landlord_profile_list(self, company_list: List[LandlordProfile], parent_log) -> None:
        """
        Perform cascade deletion for multiple company landlord profiles associated with a user.

        Args:
            company_list (List[Company]): List of company profiles to delete.
            parent_log (DeletionLog): Parent log for cascading deletions.
        """

        for company in company_list:
            self.landlord_profile(company, parent_log=parent_log)

    @abstractmethod
    def landlord_profile(self, model: LandlordProfile, reason: str,
                         parent_log: DeletionLog | None = None) -> None:
        pass

    @abstractmethod
    def single_model(self, model: DeletableModel, reason: str | None = None,
                     parent_log: DeletionLog | None = None) -> None:
        pass
