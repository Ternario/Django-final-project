from rest_framework.pagination import PageNumberPagination


class PropertyPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = None
    max_page_size = None


class ReviewPagination(PageNumberPagination):
    page_size = 40
    page_size_query_param = None
    max_page_size = None
