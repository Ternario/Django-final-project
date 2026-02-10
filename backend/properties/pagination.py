from typing import Any, Dict

import math
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class Pagination(PageNumberPagination):
    page_size: int = 15
    max_page_size: int = 70

    def get_paginated_response(self, data: Dict[str, Any]) -> Response:
        total_page: int = math.ceil(self.page.paginator.count / self.get_page_size(self.request))
        return Response({
            'count': self.page.paginator.count,
            'total_page': total_page,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
