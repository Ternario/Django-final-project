from enum import Enum

from properties.utils.choices.enumMixin import ChoicesEnumMixin


class PropertyType(ChoicesEnumMixin, Enum):
    """
    Types of properties that can be listed.

    - APARTMENT: Standard apartment unit.
    - HOUSE: Standalone house.
    - STUDIO: Studio apartment.
    - VILLA: Luxury villa.
    - PENTHOUSE: Penthouse unit.
    - HOSTEL: Hostel accommodation.
    - HOTEL: Hotel room or suite.
    """
    APARTMENT = ('APARTMENT', 'Apartment')
    HOUSE = ('HOUSE', 'House')
    STUDIO = ('STUDIO', 'Studio')
    VILLA = ('VILLA', 'Villa')
    PENTHOUSE = ('PENTHOUSE', 'Penthouse')
    HOSTEL = ('HOSTEL', 'Hostel')
    HOTEL = ('HOTEL', 'Hotel')


class PropertyAvailabilityStatus(ChoicesEnumMixin, Enum):
    """
    Statuses indicating the availability of a Property.

    - ACTIVE: The property is currently available for properties.
    - INACTIVE: The property is not available for properties.
    - UNDER_MAINTENANCE: The property is temporarily unavailable due to maintenance.
    - DELETED: The property has been removed from the system.
    - PRIVACY_REMOVED: The property is anonymized for privacy reasons.
    """

    ACTIVE = ('ACTIVE', 'Active')
    INACTIVE = ('INACTIVE', 'Inactive')
    UNDER_MAINTENANCE = ('UNDER_MAINTENANCE', 'Under maintenance')
    DELETED = ('DELETED', 'Deleted')
    PRIVACY_REMOVED = ('PRIVACY_REMOVED', 'Privacy removed')


class PropertyApprovalStatus(ChoicesEnumMixin, Enum):
    """
    Statuses representing the confirmation/moderation state of a placement.

    - PENDING: Waiting for approval.
    - AUTO_APPROVED: Automatically approved by the system.
    - MANUAL_APPROVED: Approved manually by an administrator.
    - REJECTED: Rejected after moderation review.
    """

    PENDING = ('PENDING', 'Pending')
    AUTO_APPROVED = ('AUTO_APPROVED', 'Auto approved')
    MANUAL_APPROVED = ('MANUAL_APPROVED', 'Manual approved')
    REJECTED = ('REJECTED', 'Rejected')
