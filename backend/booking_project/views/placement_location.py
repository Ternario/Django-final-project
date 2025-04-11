from rest_framework.generics import RetrieveUpdateAPIView, get_object_or_404

from booking_project.permissions import IsOwnerPlacementRelatedModels
from booking_project.models.placement_location import PlacementLocation
from booking_project.serializers.placement_location import LocationSerializer


class LocationRetrieveUpdateView(RetrieveUpdateAPIView):
    """
    View to get or update Placement Location of placement by id only for owner user.

    Example of GET request:
    GET /placement/1/location/

    Response:
    {
        'placement': 9,
        'country': 'Country nmae',
        'city': 'City name',
        'post_code': '10405',
        'street': 'Street name',
        'house_number': '1',
    }

    Example of PUT request:
    PUT /placement/1/location/

    {
        'placement': 9,
        'country': ' New country nmae',
        'city': 'New City name',
        'post_code': '40605',
        'street': 'New street name',
        'house_number': '5',
    }

    Response:
    {
        'placement': 9,
        'country': ' New country nmae',
        'city': 'New City name',
        'post_code': '40605',
        'street': 'New street name',
        'house_number': '5',
    }

    Permissions:
         - IsLandLord: can only be used by users who are landlords.
         - OnlyOwnerPlacementRelatedModels: can only be used by the owner of the Placement Location.
         - IsAuthenticated: can only be used by an authorized user.
    """

    permission_classes = [IsOwnerPlacementRelatedModels]
    serializer_class = LocationSerializer

    def get_object(self):
        placement_location = get_object_or_404(PlacementLocation, placement=self.kwargs['placement'])

        self.check_object_permissions(self.request, placement_location)

        return placement_location
