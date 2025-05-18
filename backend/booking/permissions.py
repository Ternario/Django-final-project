from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj == request.user


class IsLandLord(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_landlord


class IsOwnerPlacement(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_landlord

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsOwnerPlacementRelatedModels(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_landlord

    def has_object_permission(self, request, view, obj):
        return obj.placement.owner == request.user


class IsOwnerBooking(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsOwnerReview(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.author == request.user
