from django.db import IntegrityError
from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.generics import RetrieveUpdateAPIView, get_object_or_404, ListAPIView
from rest_framework.permissions import IsAuthenticated

from properties.models import UserProfile, User, Currency, Property
from properties.serializers import UserProfileSerializer, PropertyBaseFavoritesSerializer
from properties.utils.currency import user_currency_or_default


class UserProfileRUAV(RetrieveUpdateAPIView):
    """
    API view for retrieving and updating the profile of the authenticated user.

    - GET: retrieve the `UserProfile` object associated with the current authenticated user.
    - PUT/PATCH: update the user's profile information using the `UserProfileSerializer`.
    - Ensures that only authenticated users can access and modify their own profile.
    """
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_object(self) -> UserProfile:
        user: User = self.request.user

        return get_object_or_404(self.get_queryset(), user_id=user.pk)


class UserPropertyFavoritesListAV(ListAPIView):
    """
    API view to retrieve the authenticated user's favorite properties.

    - GET: returns a list of `Property` objects from the user's `favorites` field
      serialized with `PropertyBaseSerializer`.
    - Permissions: only authenticated users can access their favorites.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PropertyBaseFavoritesSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Property.objects.none()

        user = self.request.user
        user_profile = get_object_or_404(UserProfile, user_id=user.pk)

        return user_profile.favorites.all().select_related(
            'location'
        ).prefetch_related('property_images')

    def list(self, request, *args, **kwargs) -> Response:
        queryset: QuerySet[Property] = self.get_queryset()

        currency: Currency = user_currency_or_default(self.request)

        serializer = self.get_serializer(queryset, context={'currency': currency}, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=None,
    responses={200: None},
    description='Add / remove property by id to/ from favorites list.'
)
class UserProfileHandelFavoritesAV(APIView):
    """
    API view for managing the authenticated user's favorite properties.

    - POST: add a Property to the authenticated user's `favorites` M2M field.
      The `Property` ID must be provided in the URL (`p_id`). Returns 201 CREATED on success.
    - DELETE: remove a Property from the user's `favorites` using the `p_id` from the URL.
      Returns 204 NO CONTENT on success.
    - Permissions: only authenticated users can add or remove favorites.
    - If the specified Property does not exist, returns 404 NOT FOUND.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs) -> Response:
        user: User = request.user
        p_id: int = kwargs['p_id']

        user_profile: UserProfile = get_object_or_404(UserProfile, user_id=user.pk)

        try:
            user_profile.favorites.add(p_id)
        except IntegrityError:
            return Response({'detail': 'Property does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            {'detail': f'Property {p_id} added to favorites.'}, status=status.HTTP_201_CREATED
        )

    def delete(self, request, *args, **kwargs) -> Response:
        user: User = request.user
        p_id: int = kwargs['p_id']

        user_profile: UserProfile = get_object_or_404(UserProfile, user_id=user.pk)

        try:
            user_profile.favorites.remove(p_id)
        except IntegrityError:
            return Response({'detail': 'Property does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)
