from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from properties.models import User

from rest_framework.generics import RetrieveUpdateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated

from properties.models import UserProfile, User
from properties.serializers import UserProfileSerializer


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
