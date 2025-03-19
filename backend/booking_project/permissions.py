from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj == request.user


class IsLandLord(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return request.user.is_landlord

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return request.user.is_landlord


class OnlyOwnerPlacement(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class OnlyOwnerPlacementRelatedModels(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.placement.owner == request.user


class IsOwnerBookingPlacement(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.placement.owner == request.user


class IsOwnerBooking(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.user == request.user


class IsOwnerReview(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.author == request.user
