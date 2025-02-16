from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAdminUser

from booking_project.models.category import Category
from booking_project.serializers.category import CategoriesSerializer


class CategoryCreateListView(CreateAPIView):
    permission_classes = [AllowAny, IsAuthenticatedOrReadOnly]

    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer


class CategoryRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = CategoriesSerializer

    def get_object(self):
        return get_object_or_404(Category, pk=self.kwargs['pk'])