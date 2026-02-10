from __future__ import annotations
from typing import TYPE_CHECKING, List, Union, Tuple, Dict

if TYPE_CHECKING:
    from properties.models import User, LandlordProfile, Property, Booking

from abc import ABC, abstractmethod
from django.core.mail import send_mail, EmailMultiAlternatives, send_mass_mail
from django.template.loader import render_to_string
from base_config import settings

from properties.utils.constants.email_subjects import EMAIL_SUBJECTS

Models = Union[User, LandlordProfile, Property]


class BaseEmailResponse(ABC):
    """
    Abstract base class that provides a standardized interface and utility
    methods for sending email notifications related to cascade deletes.

    This class centralizes email generation logic, including:
    - Defining common admin error messages for different models.
    - Rendering email content (plain text and HTML) using Django templates.
    - Sending single or multiple emails via Django's email utilities.
    - Providing abstract methods to handle success, failure, and error cases
      that subclasses must implement.

    Attributes:
        ADMIN_ERROR_MESSAGE (Dict[str, str]): Mapping of model names to
            corresponding formatted error message templates.
        target_model (Models): Django model instance associated with the email context.
        target_model_name (str): The lowercase model name derived from `target_model`.
        deleted_by (str): Email address of the user who triggered the delete action.
        default_from (str): Default sender email address, loaded from Django settings.
        support_emails (Union[str, List[str]]): Support contact(s) from settings
            to receive error notifications.
    """
    ADMIN_ERROR_MESSAGE: Dict[str, str] = {
        'user': 'An error occurred during the soft cascade delete '
                'of account data of ({email}, id: {pk}) user.',
        'landlordprofile': (
            'An error occurred during the soft cascade delete of landlord profile data ({name}, id: {pk}) '
            'of ({email}, id: {user_pk}) user.'
        ),
        'property': (
            'An error occurred during the soft cascade delete '
            'of Property data ({title}, id: {pk}) of {by_profile} ({name}, id: {profile_pk}).'
        )
    }

    def __init__(self, target_model: Models, deleted_by: str) -> None:
        self.target_model = target_model
        self.target_model_name = self._get_model_name(target_model)
        self.deleted_by = deleted_by
        self.default_from = settings.DEFAULT_FROM_EMAIL
        self.support_emails = self._set_support_emails()

    @staticmethod
    def _set_support_emails():
        """
        Retrieve support email addresses from Django settings.

        Returns:
            List[str]: A list of support email addresses, normalized even if
            a single string was provided in settings.
        """
        support_emails: str | List[str] = settings.SUPPORT_EMAILS['support']

        if isinstance(support_emails, str):
            support_emails: List[str] = [support_emails]

        return support_emails

    @staticmethod
    def _get_model_name(instance: Models) -> str:
        """
        Retrieve the model name of a given Django model instance.

        Args:
            instance (models.Model): A Django model instance.

        Returns:
            str: The lowercase model name.
        """
        return instance._meta.model_name

    def _send_email(self, subject: str, message: str, emails_list: List[str] | None = None) -> None:
        """
        Send a plain text email to one or more recipients.

        Args:
            subject (str): Subject line of the email.
            message (str): Plain text body of the email.
            emails_list (Optional[List[str]]): List of recipient addresses.
                Defaults to the user who initiated the delete.
        """
        recipient_list: List[str] = [self.deleted_by] if not emails_list else emails_list

        send_mail(
            from_email=self.default_from,
            recipient_list=recipient_list,
            subject=subject,
            message=message
        )

    def _send_success(self, message: str) -> None:
        """
        Send a success notification email to a user.

        Args:
            message (str): Plain text body of the email.

        Raises:
            Exception: If the email could not be sent.
        """
        self._send_email(EMAIL_SUBJECTS['success'], message)

    def _send_failed(self, message: str, link_list: List[str], is_admin: bool = False) -> None:
        """
        Send a failure notification email with both plain text and HTML content.

        The email body is rendered from templates:
            - "emails/failed.txt" for the plain text version.
            - "emails/failed.html" for the HTML version with clickable links.

        Args:
            message (str): Main failure message.
            link_list (List[str]): List of booking URLs included in the message.
            is_admin (bool): If True, send the message to both the admin who initiated
                the deletion and the support contacts. Defaults to False (only the user).

        Raises:
            Exception: If the email could not be sent.
        """
        context = {'message': message, 'links': link_list}

        body = render_to_string('emails/failed.txt', context)
        html_content = render_to_string('emails/failed.html', context)

        if is_admin:
            recipient_list: List[str] = [self.deleted_by, *self.support_emails]
        else:
            recipient_list: List[str] = [self.deleted_by]

        email_message = EmailMultiAlternatives(
            from_email=self.default_from,
            to=recipient_list,
            subject=EMAIL_SUBJECTS['failed'],
            body=body
        )
        email_message.attach_alternative(html_content, 'text/html')
        email_message.send()

    def _send_error(self, message: str) -> None:
        """
        Send an error notification email to both the admin who initiated
        the deletion and the support contacts.

        Args:
            message (str): Plain text body of the email.

        Raises:
            Exception: If the email could not be sent.
        """
        recipient_list: List[str] = [self.deleted_by, *self.support_emails]

        self._send_email(EMAIL_SUBJECTS['error'], message, recipient_list)

    @staticmethod
    def _send_multiple_email(data: List[Tuple[str, str, str, List[str]]]) -> None:
        """
        Send multiple emails in a single call using Django's send_mass_mail.

        Args:
            data (List[Tuple[str, str, str, List[str]]]):
                A list of 4-tuples containing:
                - subject (str): Subject line of the email.
                - message (str): Plain text body of the email.
                - from_email (str): Sender email address.
                - recipient_list (List[str]): List of recipient email addresses.

        Raises:
            Exception: If one or more emails could not be sent.
        """
        send_mass_mail(data, fail_silently=False)

    @abstractmethod
    def handle_success(self) -> None:
        """
        Abstract method to handle delete success scenarios.

        Must be implemented by subclasses to define specific success
        notification behavior.
        """
        pass

    @abstractmethod
    def handle_failed(self, active_bookings: List[Booking], landlord_profile: bool) -> None:
        """
        Abstract method to handle delete failure scenarios.

        Must be implemented by subclasses to define behavior when active
        bookings or profile-related issues prevent successful deletion.

        Args:
            active_bookings (List[Booking]): List of active bookings
                blocking the delete operation.
            landlord_profile (bool): Flag indicating whether the failure
                is associated with a landlord profile.
        """
        pass

    @abstractmethod
    def handle_error(self) -> None:
        """
        Abstract method to handle unexpected error scenarios.

        Must be implemented by subclasses to define error notification
        and recovery logic.
        """
        pass
