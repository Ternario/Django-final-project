from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from booking_project.placement.models.categories import Categories
from booking_project.placement.serializers.categories_serializer import CategoriesSerializer


class CategoryCreateListView(ListAPIView):
    permission_classes = [AllowAny]

    queryset = Categories.objects.all()
    serializer_class = CategoriesSerializer
