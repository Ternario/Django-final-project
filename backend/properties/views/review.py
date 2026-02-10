from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from properties.models import User

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter
from rest_framework.generics import (
    ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404, RetrieveUpdateAPIView
)
from rest_framework.permissions import IsAuthenticated, AllowAny, SAFE_METHODS
from rest_framework.response import Response

from properties.models import Review, Booking
from properties.permissions import IsLandlord
from properties.serializers import (
    ReviewCreateSerializer, ReviewListSerializer, ReviewAuthorListSerializer, ReviewAuthorSerializer,
    ReviewPropertyOwnerSerializer
)
from properties.utils.check_permissions.related_to_property_models import CheckRelatedPropertyModelsPermission


class ReviewCAV(CreateAPIView):
    """
    API view for creating a review associated with a specific booking.

    - POST: create a new `Review` object linked to a booking identified
      by `b_id`.
    - Ensures that the requesting user is the guest of the specified booking.
    - Passes the authenticated user and booking instance to
      `ReviewCreateSerializer` via serializer context.
    - Only accessible to authenticated users (`IsAuthenticated`).

    This view ensures that only the guest who made the booking
    can create a review for it.
    """
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializer

    def create(self, request, *args, **kwargs) -> Response:
        user: User = self.request.user
        b_id: int = self.kwargs['b_id']

        booking: Booking = get_object_or_404(Booking, id=b_id, guest_id=user.pk)

        serializer: ReviewCreateSerializer = self.get_serializer(
            data=request.data, context={'user': user, 'booking': booking}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReviewPublicLAV(ListAPIView):
    """
    Public API view for listing published reviews of a specific property.

    - GET: retrieve a list of published `Review` objects linked to
      a property identified by `p_id`.
    - Supports filtering by `rating` and `created_at`.
    - Supports ordering by `rating` and `created_at`
      (default ordering: newest first).
    - Includes related fields (`owner_response_by`, `moderator_notes_by`)
      for optimized queries.
    - Accessible to any user (`AllowAny`).

    This view provides publicly visible reviews for a property.
    """
    permission_classes = [AllowAny]
    serializer_class = ReviewListSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['rating', 'created_at']
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self) -> QuerySet[Review]:
        p_id: int = self.kwargs['p_id']
        return Review.objects.published(property_ref_id=p_id).select_related('owner_response_by', 'moderator_notes_by')


class ReviewAuthorLAV(ListAPIView):
    """
    API view for listing reviews created by the authenticated user.

    - GET: retrieve a list of `Review` objects authored by the current user.
    - Supports filtering by `property_ref`, `rating`, and `created_at`.
    - Supports ordering by `rating` and `created_at`
      (default ordering: newest first).
    - Uses `select_related('property_ref')` for optimized queries.
    - Only accessible to authenticated users (`IsAuthenticated`).

    This view allows users to view and manage their own reviews.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ReviewAuthorListSerializer

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['property_ref', 'rating', 'created_at']
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self) -> QuerySet[Review]:
        user: User = self.request.user
        return Review.objects.filter(author_id=user.pk).select_related('property_ref')


class ReviewRUDAV(RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, and deleting a review
    created by the authenticated user.

    - GET: retrieve a specific `Review` identified by `r_id`,
      belonging to the authenticated user.
    - PUT/PATCH: update the review if it belongs to the user.
    - DELETE: perform a soft delete of the review using `soft_delete()`.
    - Includes related fields for safe (read-only) requests
      to optimize query performance.
    - Only accessible to authenticated users (`IsAuthenticated`).

    This view ensures that users can only access and manage
    their own reviews.
    """
    permission_classes = [IsAuthenticated]
    queryset = Review.objects.all()
    serializer_class = ReviewAuthorSerializer

    def get_object(self) -> Review:
        user: User = self.request.user
        r_id: int = self.kwargs['r_id']

        queryset: QuerySet[Review] = self.get_queryset()

        if self.request.method in SAFE_METHODS:
            queryset = queryset.select_related('owner_response_by', 'moderator_notes_by')

            return get_object_or_404(queryset, pk=r_id, author_id=user.pk)

        return get_object_or_404(queryset, pk=r_id, author_id=user.pk)

    def perform_destroy(self, instance) -> None:
        instance.soft_delete()

    def destroy(self, request, *args, **kwargs) -> Response:
        instance = self.get_object()

        self.perform_destroy(instance)

        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewPropertyOwnerRUAV(RetrieveUpdateAPIView):
    """
    API view for retrieving and updating a published review
    from the property owner's perspective.

    - GET: retrieve a published `Review` associated with a property
      identified by `p_id`, landlord `hash_id`, and review `r_id`.
    - PATCH: allow the property owner to update specific fields
      (e.g., owner response) using `ReviewPropertyOwnerSerializer`.
    - Validates that the requesting user has access to the property
      using `CheckRelatedPropertyModelsPermission`.
    - Includes related fields (`owner_response_by`, `moderator_notes_by`)
      for optimized queries on safe requests.
    - Only accessible to the property owner, company,
      or company member (`IsLandlord`).

    This view ensures that authorized property owners can
    manage responses to reviews of their property.
    """
    permission_classes = [IsLandlord]
    queryset = Review.objects.published()
    serializer_class = ReviewPropertyOwnerSerializer

    def get_object(self):
        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']
        p_id: int = self.kwargs['p_id']
        r_id: int = self.kwargs['r_id']

        CheckRelatedPropertyModelsPermission(user, hash_id, p_id).access()

        queryset: QuerySet[Review] = self.get_queryset()

        if self.request.method in SAFE_METHODS:
            queryset = queryset.select_related('owner_response_by', 'moderator_notes_by')

            return get_object_or_404(queryset, pk=r_id, property_ref_id=p_id, property_ref__owner__hash_id=hash_id)

        return get_object_or_404(queryset, pk=r_id, property_ref_id=p_id, property_ref__owner__hash_id=hash_id)

    def update(self, request, *args, **kwargs) -> Response:
        instance: Review = self.get_object()
        user: User = self.request.user

        serializer: ReviewPropertyOwnerSerializer = self.get_serializer(
            instance=instance, data=self.request.data, context={'user': user}, partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status.HTTP_200_OK)
