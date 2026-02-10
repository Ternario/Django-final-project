from typing import TYPE_CHECKING, List, Union, Tuple, Dict

if TYPE_CHECKING:
    from properties.models import User, LandlordProfile, Property, Booking

from properties.services.delete.email.base import BaseEmailResponse
from properties.services.delete.class_mixin.email import EmailResponseMixin
from properties.utils.constants.email_subjects import EMAIL_SUBJECTS
from properties.utils.decorators import key_error

Models = Union[User, LandlordProfile, Property]


class SoftUserResponse(BaseEmailResponse, EmailResponseMixin):
    """
    Handles email notifications for soft deletion actions initiated by the owner of a model.

    This class is a subclass of `BaseEmailResponse` and is responsible for sending
    success, failure, and error emails to users and support staff when a user deletes
    their own account, landlord, company, or property data.

    Attributes:
        SUCCESS_MESSAGES (Dict[str, str]): Templates for success messages per model type.
        FAILED_MESSAGES (Dict[str, str]): Templates for failure messages when deletion is blocked by active bookings.
        ERROR_MESSAGES (Dict[str, str]): Templates for error messages to notify the user in case of deletion failure.
    """
    SUCCESS_MESSAGES: Dict[str, str] = {
        'user': 'Your account data was successfully deleted.',
        'landlordprofile': 'Your landlord profile ({name}) was successfully deleted.',
        'property': 'Your Property ({title}) was successfully deleted.'
    }

    FAILED_MESSAGES = {
        'user': f'Property /ies have active bookings and cannot be deleted. Please check the links below:',
        'landlordprofile': (
            f'Your Property/ies have active bookings and cannot be deleted. Please check the links below:'
        ),
        'property': f'Your Property have active bookings and cannot be deleted. Please check the links below:'
    }

    ERROR_MESSAGES = {
        'user': 'An error occurred while deleting your account data, please contact us by email.',
        'landlordprofile': 'An error occurred while deleting your landlord ({name}) data, please contact us by email.',
        'property': 'An error occurred while deleting your Property ({title}) data please contact us by email.'
    }

    def _set_user_message_data(self, message: str) -> str:
        """
        Format a message template with model-specific data.

        Args:
            message (str): The message template containing placeholders for model attributes.

        Returns:
            str: The formatted message with the model-specific information filled in.
        """

        if isinstance(self.target_model, LandlordProfile):
            formatted_message: str = message.format(name=self.target_model.name)
        else:
            formatted_message: str = message.format(title=self.target_model.title)

        return formatted_message

    def _get_message(self, templ_dict: Dict) -> str:
        """
        Retrieve and format the message for the current model using the provided template dictionary.

        Args:
            templ_dict (Dict): A dictionary mapping model names to message templates.

        Returns:
            str: The message ready to be sent to the user, formatted with model-specific data.
        """
        if not isinstance(self.target_model, User):
            get_message: str = templ_dict[self.target_model_name]
            message: str = self._set_user_message_data(get_message)
        else:
            message: str = templ_dict[self.target_model_name]

        return message

    @key_error
    def handle_success(self) -> None:
        """
        Send a success email to the user after successful deletion of their own model.

        Uses the SUCCESS_MESSAGES dictionary to generate the appropriate message
        for the model type.

        Raises:
            Logs any KeyError or Exception encountered during message sending using `@key_error`.
        """
        message: str = self._get_message(self.SUCCESS_MESSAGES)

        self._send_success(message)

    @key_error
    def handle_failed(self, active_bookings: List[Booking], landlord_profile: bool = False) -> None:
        """
        Send a failure email to the user when deletion is blocked by active bookings.

        The message is customized for the user and optionally includes
        information about related landlord profiles.

        Args:
            active_bookings (List[Booking]): List of active bookings preventing deletion.
            landlord_profile (bool | None): Indicates if the user owns the associated landlord profile.

        Raises:
            Logs any KeyError or Exception encountered during message sending using `@key_error`.
        """
        message: str = self.FAILED_MESSAGES[self.target_model_name]

        if isinstance(self.target_model, User):
            if landlord_profile:
                message = f'You or your {message}'
            message = f'You {message}'

        booking_links: List[str] = self._build_bookings_list(bookings=active_bookings, same_user=True, role='owner')

        self._send_failed(message, booking_links)

    @key_error
    def handle_error(self) -> None:
        """
        Send an error email to both the user and support staff when deletion fails due to unexpected issues.

        Generates separate messages:
            - User message from ERROR_MESSAGES.
            - Admin/support message from ADMIN_ERROR_MESSAGE including a timestamp.

        Raises:
            Logs any KeyError or Exception encountered during message sending using `@key_error`.
        """
        user_message: str = self._get_message(self.ERROR_MESSAGES)

        get_admin_message: str = self.ADMIN_ERROR_MESSAGE[self.target_model_name]
        result: str = self._set_message_data(get_admin_message)
        admin_message = result

        timestamp: str = self._get_message_datetime()
        admin_message = f'{admin_message} {timestamp}'

        data: List[Tuple[str, str, str, List[str]]] = [
            (EMAIL_SUBJECTS['error'], user_message, self.default_from, [self.deleted_by]),
            (EMAIL_SUBJECTS['error'], admin_message, self.default_from, self.support_emails),
        ]

        self._send_multiple_email(data)
