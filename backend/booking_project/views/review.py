from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from booking_project.permissions import IsOwnerReview
from booking_project.serializers.review import *


class ReviewCreateView(CreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Review.objects.all()
    serializer_class = RatingSerializer


class ReviewListView(ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Review.objects.all()
    serializer_class = RatingSerializer
    lookup_field = 'pk'


class ReviewUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerReview, IsAuthenticatedOrReadOnly]
    queryset = Review.objects.all()
    serializer_class = ReviewUpdateSerializer
    lookup_field = 'pk'
