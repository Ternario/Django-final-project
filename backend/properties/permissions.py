from rest_framework.permissions import BasePermission, SAFE_METHODS


class StaffOnly(BasePermission):
    """
    Allows access only to staff users.
    """

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.is_staff)


class IsOwnerDiscountUser(BasePermission):
    """
    Allows access only to the discount_user owner user.
    """

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return bool(obj.user == request.user)


class IsOwnerUser(BasePermission):
    """
    Allows access only to the owner of the user object.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj == request.user


class IsLandlord(BasePermission):
    """
    Allows access only to landlord users.
    """

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.is_landlord)


class IsOwnerBooking(BasePermission):
    """
    Allows access only to the booking owner user.
    """

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return bool(obj.guest == request.user)
