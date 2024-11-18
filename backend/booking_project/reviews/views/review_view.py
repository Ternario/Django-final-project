from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from booking_project.permissions import IsOwnerReview
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
    permission_classes = [IsOwnerReview, IsAuthenticatedOrReadOnly]
    queryset = Review.objects.all()
    serializer_class = ReviewUpdateSerializer
    lookup_field = 'pk'


class ReviewDestroyView(DestroyAPIView):
    permission_classes = [IsOwnerReview, IsAuthenticated]
    queryset = Review.objects.all()
    lookup_field = 'pk'
