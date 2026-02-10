from __future__ import annotations
from typing import List, Tuple, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from properties.models import Booking

from properties.services.delete.email.base import BaseEmailResponse
from properties.services.delete.class_mixin.email import EmailResponseMixin
from properties.utils.constants.email_subjects import EMAIL_SUBJECTS
from properties.utils.decorators import key_error


class PrivacyAdminResponse(BaseEmailResponse, EmailResponseMixin):
    """
    Handles email notifications for privacy-based user depersonalization actions.

    Supports:
        - Sending success notifications to both admins and the affected user.
        - Sending failure notifications with details about active bookings.
        - Sending error notifications in case of unexpected issues.

    Attributes:
        SUCCESS_MESSAGE (str): Template message for successful depersonalization (admin view).
        SUCCESS_USER_MESSAGE (str): Template message for successful depersonalization (user view).
        FAILED_MESSAGE (str): Template message when depersonalization fails due to active bookings.
        ERROR_MESSAGE (str): Template message for unexpected errors during depersonalization.
    """
    SUCCESS_MESSAGE: str = 'User ({email}, id: {pk}) was successfully Depersonalised.'
    SUCCESS_USER_MESSAGE: str = (
        'Your account data was depersonalised by administration. For questions and details, please contact us by email.'
    )
    FAILED_MESSAGE: str = 'User ({email}, id: {pk}) {is_property}has active bookings and cannot be deleted.'
    ERROR_MESSAGE: str = (
        'An error occurred during the privacy cascade delete of account data of ({email}, id: {pk}) user.'
    )

    @key_error
    def handle_success(self) -> None:
        """
        Send success notifications after successful depersonalization.

        Emails sent:
            - Admin notification with timestamp.
            - User notification about account depersonalization.

        Raises:
            Logs any KeyError or Exception encountered during message sending using `@key_error`.
        """
        context: Dict[str, str | int] = {
            'email': self.target_model.email,
            'pk': self.target_model.pk,
        }
        admin_message: str = self.SUCCESS_MESSAGE.format(**context)
        user_message: str = self.SUCCESS_USER_MESSAGE

        timestamp: str = self._get_message_datetime()
        admin_message = f'{admin_message} {timestamp}'

        data: List[Tuple[str, str, str, List[str]]] = [
            (EMAIL_SUBJECTS['success'], admin_message, self.default_from, [self.deleted_by, *self.support_emails]),
            (EMAIL_SUBJECTS['success'], user_message, self.default_from, [self.target_model.email])
        ]

        self._send_multiple_email(data)

    @key_error
    def handle_failed(self, active_bookings: List[Booking], landlord_profile: bool = False) -> None:
        """
        Send failure notification when depersonalization cannot proceed due to active bookings.

        Args:
            active_bookings (List[Booking]): List of active bookings blocking deletion.
            landlord_profile (bool): Whether the user is a landlord (adds property info to message).

        Raises:
            Logs any KeyError or Exception encountered during message sending using `@key_error`.
        """
        context: Dict[str, str | int] = {
            'email': self.target_model.email,
            'pk': self.target_model.pk,
            'is_property': 'or his Property' if landlord_profile else ''
        }
        message: str = self.FAILED_MESSAGE.format(**context)

        timestamp: str = self._get_message_datetime()
        message = f'{message} {timestamp}'

        booking_links: List[str] = self._build_bookings_list(bookings=active_bookings, same_user=False)

        self._send_failed(message, booking_links, is_admin=True)

    @key_error
    def handle_error(self) -> None:
        """
        Send an error notification email to the administrator and support contacts.

        The email includes details of an unexpected failure during depersonalization.
        A timestamp is appended to the message.
        """
        context: Dict[str, str | int] = {
            'email': self.target_model.email,
            'pk': self.target_model.pk,
        }

        message: str = self.ERROR_MESSAGE.format(**context)

        timestamp: str = self._get_message_datetime()
        message = f'{message} {timestamp}'

        self._send_error(message)
