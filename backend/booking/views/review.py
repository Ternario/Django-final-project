from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from booking.models import Review
from booking.permissions import IsOwnerReview
from booking.serializers.review import ReviewCreateSerializer, ReviewUpdateSerializer


class ReviewCreateView(CreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Review.objects.all()
    serializer_class = ReviewCreateSerializer


class ReviewListView(ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Review.objects.all()
    serializer_class = ReviewUpdateSerializer
    lookup_field = 'pk'


class ReviewUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerReview, IsAuthenticatedOrReadOnly]
    queryset = Review.objects.all()
    serializer_class = ReviewUpdateSerializer
    lookup_field = 'pk'
