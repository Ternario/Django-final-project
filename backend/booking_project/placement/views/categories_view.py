from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly

from booking_project.placement.models.categories import Categories
from booking_project.placement.serializers.categories_serializer import CategoriesSerializer


class CategoryCreateListView(ListCreateAPIView):
    permission_classes = [IsAdminUser, IsAuthenticatedOrReadOnly]

    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer


