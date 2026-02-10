from enum import Enum

from properties.utils.choices.enumMixin import ChoicesEnumMixin


class LandlordType(ChoicesEnumMixin, Enum):
    """
    Types of landlords in the system.

    - INDIVIDUAL: An individual landlord.
    - COMPANY: A company acting as a landlord.
    - COMPANY_MEMBER: A user who is a member of a landlord company.
    - NONE: No landlord type assigned.
    """
    INDIVIDUAL = ('INDIVIDUAL', 'Individual')
    COMPANY = ('COMPANY', 'Company')
    COMPANY_MEMBER = ('COMPANY_MEMBER', 'Member of an company')
    NONE = ('NONE', 'None')


class CompanyRole(ChoicesEnumMixin, Enum):
    """
    Roles of users within a company.

    - ADMIN: Company administrator with full access.
    - MANAGER: Manager with limited permissions.
    - ACCOUNTANT: Accountant responsible for financial tasks.
    """
    ADMIN = ('ADMIN', 'Admin')
    MANAGER = ('MANAGER', 'Manager')
    ACCOUNTANT = ('ACCOUNTANT', 'Accountant')
