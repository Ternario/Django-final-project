from rest_framework.generics import RetrieveUpdateAPIView, get_object_or_404

from booking.permissions import IsOwnerPlacementRelatedModels
from booking.models.placement_details import PlacementDetails
from booking.serializers.placement_details import PlacementDetailSerializer


class PlacementDetailsRetrieveUpdateView(RetrieveUpdateAPIView):
    """
    View to get or update Placement Details of placement by id only for owner user.

    Example of GET request:
    GET /placement/1/details/

    Response:
    {
        'placement': 9,
        'pets': True,
        'free_wifi': False,
        'smoking': False,
        'parking': False,
        'room_service': True,
        'front_desk_allowed_24': False,
        'free_cancellation': False,
        'balcony': True,
        'air_conditioning': False,
        'washing_machine': False,
        'kitchenette': False,
        'tv': False,
        'coffee_tee_maker': True,
    }

    Example of PUT request:
    PUT /placement/1/details/

    {
        'placement': 9,
        'pets': False,
        'free_wifi': False,
        'smoking': False,
        'parking': True,
        'room_service': True,
        'front_desk_allowed_24': True,
        'free_cancellation': True,
        'balcony': True,
        'air_conditioning': False,
        'washing_machine': False,
        'kitchenette': False,
        'tv': False,
        'coffee_tee_maker': False,
    }

    Response:
    {
        'placement': 9,
        'pets': False,
        'free_wifi': False,
        'smoking': False,
        'parking': True,
        'room_service': True,
        'front_desk_allowed_24': True,
        'free_cancellation': True,
        'balcony': True,
        'air_conditioning': False,
        'washing_machine': False,
        'kitchenette': False,
        'tv': False,
        'coffee_tee_maker': False,
    }

    Permissions:
         - IsLandLord: can only be used by users who are landlords.
         - OnlyOwnerPlacementRelatedModels: can only be used by the owner of the Placement Details.
         - IsAuthenticated: can only be used by an authorized user.
    """
    permission_classes = [IsOwnerPlacementRelatedModels]
    serializer_class = PlacementDetailSerializer

    def get_object(self):
        placement_details = get_object_or_404(PlacementDetails, placement=self.kwargs['placement'])

        self.check_object_permissions(self.request, placement_details)

        return placement_details
