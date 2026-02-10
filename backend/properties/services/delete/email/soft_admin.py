from __future__ import annotations
from typing import TYPE_CHECKING, List, Union, Tuple, Dict

if TYPE_CHECKING:
    from properties.models import User, LandlordProfile, Property, Booking

from properties.services.delete.class_mixin.email import EmailResponseMixin
from properties.services.delete.email.base import BaseEmailResponse
from properties.utils.constants.email_subjects import EMAIL_SUBJECTS
from properties.utils.decorators import key_error

Models = Union[User, LandlordProfile, Property]


class SoftAdminResponse(BaseEmailResponse, EmailResponseMixin):
    """
    Handles email notifications for soft deletion actions initiated by an admin.

    This class extends the base email response logic with predefined
    templates and context-specific formatting for both administrators
    and end users. It generates different responses depending on whether
    a deletion succeeded, failed due to active bookings, or encountered
    an error.

    Attributes:
        SUCCESS_MESSAGE (Dict[str, str]): Templates for admin success messages per model type.
        SUCCESS_USER_MESSAGE (Dict[str, str]): Templates for user-facing success messages per model type.
        FAILED_MESSAGES (Dict[str, str]): Templates for failure messages when deletion is blocked by active bookings.
    """
    SUCCESS_MESSAGE: Dict[str, str] = {
        'user': 'User ({email}, id: {pk}) was successfully deleted.',
        'landlordprofile': (
            'Landlord profile ({name}, id: {pk}) by ({email}, id: {user_pk}) user was successfully deleted.'
        ),
        'property': 'Property ({title}, id: {pk}) by {by_profile} ({name}, id: {profile_pk}) was successfully deleted.'
    }

    SUCCESS_USER_MESSAGE: Dict[str, str] = {
        'user': (
            'Your account data was deleted by administration. For questions and details, please contact us by email.'
        ),
        'landlordprofile': (
            'Your landlord profile ({name}) was deleted by administration. '
            'For questions and details, please contact us by email.'
        ),
        'property': (
            'Your Property ({title}) by {by_profile} ({name}) was deleted by administration. '
            'For questions and details, please contact us by email.'
        )
    }

    FAILED_MESSAGES: Dict[str, str] = {
        'user': 'User ({email}, id: {pk}) {is_property}has active bookings and cannot be deleted.',
        'landlordprofile': (
            'Landlord profile ({name}, id: {pk}) of ({email}, id: {user_pk}) user '
            'has active property bookings and cannot be deleted.'
        ),
        'property': (
            'Property ({title}, id: {pk}) by {by_profile} ({name}, id: {profile_pk}) '
            'has active property bookings and cannot be deleted.'
        )
    }

    def __init__(self, target_model: Models, deleted_by: str) -> None:
        super().__init__(target_model, deleted_by)
        self.target_email: str = self._get_target_email()

    def _get_target_email(self):
        """
        Retrieve the email address associated with the target model.

        For Property instances, returns the owner's email (individual or company).
        For other models, returns the email attribute of the target instance.

        Returns:
            str: Email address of the target or its owner.
        """
        if not isinstance(self.target_model, Property):
            return self.target_model.email

        return self.target_model.owner.email

    def _get_success_messages(self) -> Tuple[str, str]:
        """
        Generate both the administrator and user success messages.

        Returns:
            Tuple[str, str]:
                - First element: Admin success message.
                - Second element: User-facing success message.
        """
        if isinstance(self.target_model, User):
            get_admin_message: str = self.SUCCESS_MESSAGE[self.target_model_name]

            admin_message: str = self._set_message_data(get_admin_message)
            user_message: str = self.SUCCESS_USER_MESSAGE[self.target_model_name]
        else:
            get_admin_message: str = self.SUCCESS_MESSAGE[self.target_model_name]
            get_user_message: str = self.SUCCESS_USER_MESSAGE[self.target_model_name]

            admin_message: str = self._set_message_data(get_admin_message)
            user_message: str = self._set_message_data(get_user_message)

        return admin_message, user_message

    def _get_failed_user_data(self, message: str, landlord_profile: bool = False) -> str:
        """
        Format a failure message for the user model.

        Args:
            message (str): Failure message template.
            landlord_profile (bool): If True, specifies that the failure is due to landlord properties.

        Returns:
            str: Formatted failure message.
        """
        context: Dict[str, str | int] = {
            'email': self.target_model.email,
            'pk': self.target_model.pk,
            'is_property': 'or his Property' if landlord_profile else ''
        }

        return message.format(**context)

    @key_error
    def handle_success(self) -> None:
        """
        Send success emails to both administrator and user after a successful deletion.

        Adds a timestamp to the administrator's message.
        Emails are sent via `_send_multiple_email` to both admin/support and target user.
        """
        messages: Tuple[str, str] = self._get_success_messages()
        admin_message, user_message = messages

        timestamp: str = self._get_message_datetime()
        admin_message = f'{admin_message} {timestamp}'

        data: List[Tuple[str, str, str, List[str]]] = [
            (EMAIL_SUBJECTS['success'], admin_message, self.default_from, [self.deleted_by, *self.support_emails]),
            (EMAIL_SUBJECTS['success'], user_message, self.default_from, [self.target_email])
        ]

        self._send_multiple_email(data)

    @key_error
    def handle_failed(self, active_bookings: List[Booking], landlord_profile: bool = False) -> None:
        """
        Send a failure notification email to the administrator when deletion is blocked.

        The email includes details about active bookings preventing deletion.

        Args:
            active_bookings (List[Booking]): List of active bookings preventing deletion.
            landlord_profile (bool): Indicates whether the target is a landlord profile.
        """
        get_message: str = self.FAILED_MESSAGES[self.target_model_name]

        if isinstance(self.target_model, User) and landlord_profile:
            message: str = self._get_failed_user_data(get_message, landlord_profile)
        else:
            message: str = self._set_message_data(get_message)

        timestamp: str = self._get_message_datetime()
        message = f'{message} {timestamp}'

        booking_links: List[str] = self._build_bookings_list(bookings=active_bookings, same_user=False)

        self._send_failed(message, booking_links, is_admin=True)

    @key_error
    def handle_error(self) -> None:
        """
        Send an error notification email to the administrator and support contacts.

        The email includes details of an unexpected failure during deletion.
        A timestamp is appended to the message.
        """
        get_message: str = self.ADMIN_ERROR_MESSAGE[self.target_model_name]
        message: str = self._set_message_data(get_message)

        timestamp: str = self._get_message_datetime()
        message = f'{message} {timestamp}'

        self._send_error(message)
