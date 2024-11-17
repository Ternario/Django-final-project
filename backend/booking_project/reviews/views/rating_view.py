from rest_framework.exceptions import NotFound
from rest_framework.generics import ListCreateAPIView, ListAPIView, CreateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from booking_project.reviews.serializers.review_serializer import *


class ReviewCreateView(CreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Review.objects.all()
    serializer_class = RatingSerializer


class ReviewListView(ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Review.objects.all()
    serializer_class = RatingSerializer
    lookup_field = 'pk'


class ReviewUpdateView(UpdateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Review.objects.all()
    serializer_class = ReviewUpdateSerializer
    lookup_field = 'pk'
