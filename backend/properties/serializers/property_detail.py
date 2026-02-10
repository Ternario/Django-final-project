from __future__ import annotations

from typing import Any, TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from properties.models import Property

from rest_framework.serializers import ModelSerializer, CharField, ValidationError

from properties.models import PropertyDetail
from properties.utils.choices.property import PropertyType
from properties.utils.error_messages.not_null_field import NOT_NULL_FIELD
from properties.utils.error_messages.property_details import PROPERTY_DETAILS_ERRORS


class PropertyDetailCreateSerializer(ModelSerializer):
    bathroom_access_display = CharField(source='get_bathroom_access_display', read_only=True)
    kitchen_access_display = CharField(source='get_kitchen_access_display', read_only=True)
    terrace_access_display = CharField(source='get_terrace_access_display', read_only=True)
    garden_access_display = CharField(source='get_garden_access_display', read_only=True)
    check_in_from_display = CharField(source='get_check_in_from_display', read_only=True)
    check_out_until_display = CharField(source='get_check_out_until_display', read_only=True)

    class Meta:
        model = PropertyDetail
        exclude = ['created_at', 'updated_at']
        read_only_fields = ['property_ref']

    def create(self, validated_data: Dict[str, Any]) -> PropertyDetail:
        property_ref: Property = self.context['property_ref']

        validated_data['property_ref'] = property_ref

        return super().create(validated_data)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        property_ref: Property = self.context['property_ref']
        single_beds: int | None = attrs.get('single_beds', None)
        double_beds: int | None = attrs.get('double_beds', None)
        sofa_beds: int | None = attrs.get('sofa_beds', None)
        total_beds: int | None = attrs.get('total_beds', None)
        floor: int | None = attrs.get('total_beds', None)
        total_floors: int | None = attrs.get('total_beds', None)

        non_field_errors: List[str] = []

        if not (single_beds or double_beds or sofa_beds):
            non_field_errors.append(PROPERTY_DETAILS_ERRORS['beds'])

        if total_beds != (single_beds + double_beds + sofa_beds):
            non_field_errors.append(PROPERTY_DETAILS_ERRORS['total_beds'])

        if property_ref.property_type not in [PropertyType.HOUSE.value[0], PropertyType.VILLA.value[0]]:

            if not floor or not total_floors:
                non_field_errors.append(PROPERTY_DETAILS_ERRORS['empty_floors'])
            elif floor < -1 or floor > total_floors:
                non_field_errors.append(PROPERTY_DETAILS_ERRORS['floor'].format(total_floors=total_floors))

        if non_field_errors:
            raise ValidationError({'non_field_errors': non_field_errors})

        return attrs


class PropertyDetailSerializer(PropertyDetailCreateSerializer):
    class Meta:
        model = PropertyDetail
        exclude = ['created_at', 'updated_at']
        read_only_fields = ['property_ref']

    def update(self, instance: PropertyDetail, validated_data: Dict[str, Any]) -> PropertyDetail:
        validated_data.pop('property_ref', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        property_data: Property | None = self.instance.property_ref
        single_beds: int | None = attrs.get('single_beds', None)
        double_beds: int | None = attrs.get('double_beds', None)
        sofa_beds: int | None = attrs.get('sofa_beds', None)
        total_beds: int | None = attrs.get('total_beds', None)
        floor: int | None = attrs.get('floor', None)
        total_floors: int | None = attrs.get('total_floors', None)

        if not property_data:
            raise ValidationError({'property_ref', NOT_NULL_FIELD})

        non_field_errors: List[str] = []

        if any([single_beds, double_beds, sofa_beds]):
            single_beds = single_beds if single_beds else self.instance.single_bed
            double_beds = double_beds if double_beds else self.instance.double_beds
            sofa_beds = sofa_beds if sofa_beds else self.instance.sofa_beds
            total_beds = total_beds if total_beds else self.instance.total_beds

            if total_beds != (single_beds + double_beds + sofa_beds):
                non_field_errors.append(PROPERTY_DETAILS_ERRORS['total_beds'])

        if (
                (floor or total_floors)
                and
                (property_data.property_type not in [PropertyType.HOUSE.value[0], PropertyType.VILLA.value[0]])
        ):
            floor = floor if floor else self.instance.floor
            total_floors = total_floors if total_floors else self.instance.total_floors

            if floor < -1 or floor > total_floors:
                non_field_errors.append(PROPERTY_DETAILS_ERRORS['floor'].format(total_floors=total_floors))

        if non_field_errors:
            raise ValidationError({'non_field_errors': non_field_errors})

        return attrs
