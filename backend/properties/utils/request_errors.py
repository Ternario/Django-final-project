from rest_framework.exceptions import APIException


class ExternalServiceError(APIException):
    status_code = 502
    default_detail = 'Error accessing external service. Please try again later.'
    default_code = 'external_service_error'
