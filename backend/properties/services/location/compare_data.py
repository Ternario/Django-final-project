from __future__ import annotations

from typing import Dict, Any, List

import logging
import requests

from requests import Response
from rest_framework.exceptions import ValidationError

from base_config.settings import GEOAPIFY_API_KEY
from properties.models import Country, Region
from properties.utils.error_messages.location import LOCATION_ERRORS
from properties.utils.request_errors import ExternalServiceError

logger = logging.getLogger(__name__)


class CompareLocationData:
    """
    Service class for validating and comparing address data using an external geolocation API.

    This class is responsible for:
        - Normalizing input address fields.
        - Querying the Geoapify geocoding API to retrieve standardized location data.
        - Comparing the provided address with the API results and calculating confidence.
        - Raising detailed validation errors if confidence is low or fields mismatch.
        - Wrapping external request failures in a custom `ExternalServiceError`.

    Attributes:
        country (str | None): Normalized country name.
        city (str | None): Normalized city name.
        post_code (str | None): Normalized postal code.
        street (str | None): Normalized street name.
        house_number (str | None): Normalized house number.
        region (str | None): Normalized region/state name, optional.

    Raises:
        ValidationError: If the provided address fields do not match the API results
                         or the API returns insufficient confidence.
        ExternalServiceError: If the external geolocation service fails or returns an error.
    """

    def __init__(self, country: Country, city: str, post_code: str, street: str, house_number: str,
                 region: Region | None = None) -> None:
        self.country = self._normalise_result(country.name)
        self.city = self._normalise_result(city)
        self.post_code = self._normalise_result(post_code)
        self.street = self._normalise_result(street)
        self.house_number = self._normalise_result(house_number)
        self.region = self._normalise_result(region.name)

    def _request(self) -> Dict[str, Any]:
        """
        Make a request to the Geoapify geocoding API to retrieve location data.

        Returns:
            dict: JSON response from the API.

        Raises:
            ExternalServiceError: If the API request fails or returns an HTTP error.
        """

        try:
            response: Response = requests.get(
                f'https://api.geoapify.com/v1/geocode/search?',
                params={
                    'country': self.country,
                    'city': self.city,
                    'postcode': self.post_code,
                    'street': self.street,
                    'housenumber': self.house_number,
                    'lang': 'en',
                    'type': 'amenity',
                    'format': 'json',
                    'apiKey': GEOAPIFY_API_KEY,
                },

                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.exception(f'Geoapify request failed: {e}')
            raise ExternalServiceError

    @staticmethod
    def _normalise_result(value: str | None) -> str | None:
        """
        Normalize a string value by stripping whitespace and converting to lowercase.

        Args:
            value (str | None): Input string to normalize.

        Returns:
            str | None: Normalized string, or None if input is None.
        """
        return value.lower().strip() if value else None

    def compare(self):
        """
        Compare the provided address against the results from the geolocation API.

        Steps:
            1. Query the external API via `_request`.
            2. Check if results are returned; raise ValidationError if none.
            3. Compute confidence from the API's ranking.
            4. Compare input fields with API results if confidence is moderate (0.5–0.9).
            5. Raise ValidationError for mismatched fields or low confidence.
            6. Return the normalized and validated location data if confidence is high.

        Returns:
            dict: Normalized and validated location data including latitude and longitude.

        Raises:
            ValidationError: If no results are found, confidence is too low,
                             or individual fields do not match.
        """
        results: Dict[str, List[Dict[str, Any]]] = self._request()

        if not results.get('results', None):
            raise ValidationError({'data': LOCATION_ERRORS['data']})

        data_dict: Dict[str, Any] = results['results'][0]
        confidence: int = data_dict['rank']['confidence']

        result_data: Dict[str, str | None] = {
            'country': data_dict.get('country', None),
            'region': data_dict.get('region', None),
            'city': data_dict.get('city', None),
            'post_code': data_dict.get('postcode', None),
            'street': data_dict.get('street', None),
            'house_number': data_dict.get('housenumber', None),
            'latitude': data_dict.get('lat', None),
            'longitude': data_dict.get('lon', None)
        }

        errors: Dict[str, str] = {}

        if 0.9 <= confidence <= 1:
            return result_data

        elif 0.5 <= confidence < 0.9:
            if self.country != self._normalise_result(result_data['country']):
                errors['region'] = LOCATION_ERRORS['field']

            if self.region and self.region != self._normalise_result(result_data['region']):
                errors['region'] = LOCATION_ERRORS['field']

            if self.city != self._normalise_result(result_data['city']):
                errors['city'] = LOCATION_ERRORS['field']

            if self.post_code != self._normalise_result(result_data['post_code']):
                errors['post_code'] = LOCATION_ERRORS['field']

            if self.street != self._normalise_result(result_data['street']):
                errors['street'] = LOCATION_ERRORS['field']

            if self.house_number != self._normalise_result(result_data['house_number']):
                errors['house_number'] = LOCATION_ERRORS['field']

            if errors:
                raise ValidationError(errors)

            return result_data

        else:
            raise ValidationError({'confidence': LOCATION_ERRORS['confidence']})
