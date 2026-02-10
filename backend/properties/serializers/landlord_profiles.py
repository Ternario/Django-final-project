from __future__ import annotations

from typing import Any, TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from properties.models import PaymentMethod, User, Language, Currency

from rest_framework.serializers import ModelSerializer, CharField
from rest_framework.exceptions import ValidationError

from properties.models import LandlordProfile, CompanyMembership

from properties.serializers.language import LanguageSerializer
from properties.serializers.currency import CurrencyBaseSerializer
from properties.serializers.payment_method import PaymentMethodSerializer
from properties.serializers.user import UserBasePublicSerializer

from properties.utils.serializers.landlord_profile import (
    PKLanguagesList, PKCurrenciesList, PKPaymentMethodsList, check_m2m_conflict, handle_m2m_field
)
from properties.utils.error_messages.landlord_profile import LANDLORD_PROFILE_ERRORS
from properties.utils.choices.landlord_profile import LandlordType
from properties.utils.decorators import atomic_handel
from properties.utils.regex_patterns import match_phone_number


class LandlordProfileCreateSerializer(ModelSerializer):
    class Meta:
        model = LandlordProfile
        exclude = ['created_by_token', 'is_trusted', 'is_verified', 'is_deleted', 'deleted_at', 'updated_at']
        read_only_fields = ['created_by', 'hash_id']

    @atomic_handel
    def create(self, validated_data: Dict[str, Any]) -> LandlordProfile:
        validated_data['created_by'] = self.context['user']

        return super().create(validated_data)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        created_by: User = self.context['user']
        landlord_type: str = attrs.get('type')
        phone: str = attrs.get('phone')
        name: str = attrs.get('user_full_name')

        errors: Dict[str, str | List[str]] = {}
        non_field_errors: List[str] = []

        if not match_phone_number(phone):
            errors['phone'] = LANDLORD_PROFILE_ERRORS['phone']

        if (
                landlord_type == LandlordType.INDIVIDUAL.value[0]
                and
                name != f'{created_by.first_name} {created_by.last_name}'
        ):
            non_field_errors.append(LANDLORD_PROFILE_ERRORS['user_full_name'])

        if non_field_errors:
            errors['non_field_errors'] = non_field_errors

        if errors:
            raise ValidationError(errors)

        return attrs


class LandlordProfileBaseSerializer(ModelSerializer):
    class Meta:
        model = LandlordProfile
        fields = ['id', 'hash_id', 'name']


class LandlordProfilePublicSerializer(ModelSerializer):
    type_display = CharField(source='get_type_display', read_only=True)
    languages_spoken = LanguageSerializer(many=True, read_only=True)
    accepted_currencies = CurrencyBaseSerializer(many=True, read_only=True)
    default_currency = CurrencyBaseSerializer(read_only=True)
    available_payment_methods = PaymentMethodSerializer(many=True, read_only=True)

    class Meta:
        model = LandlordProfile
        fields = ['name', 'type', 'type_display', 'description', 'languages_spoken', 'accepted_currencies',
                  'default_currency', 'available_payment_methods']


class LandlordProfileSerializer(LandlordProfilePublicSerializer):
    add_languages_spoken = PKLanguagesList()
    remove_languages_spoken = PKLanguagesList()

    add_accepted_currencies = PKCurrenciesList()
    remove_accepted_currencies = PKCurrenciesList()

    add_available_payment_methods = PKPaymentMethodsList()
    remove_available_payment_methods = PKPaymentMethodsList()

    class Meta:
        model = LandlordProfile
        exclude = ['created_by_token', 'is_trusted', 'is_deleted', 'deleted_at', 'updated_at']
        read_only_fields = ['hash_id', 'created_by', 'type']

    @atomic_handel
    def update(self, instance: LandlordProfile, validated_data: Dict[str, Any]) -> LandlordProfile:
        add_languages_spoken: List[Language] = validated_data.pop('add_languages_spoken', [])
        remove_languages_spoken: List[Language] = validated_data.pop('remove_languages_spoken', [])

        add_accepted_currencies: List[Currency] = validated_data.pop('add_accepted_currencies', [])
        remove_accepted_currencies: List[Currency] = validated_data.pop('remove_accepted_currencies', [])

        add_available_payment_methods: List[PaymentMethod] = validated_data.pop('add_available_payment_methods', [])
        remove_available_payment_methods: List[PaymentMethod] = validated_data.pop('remove_available_payment_methods',
                                                                                   [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        handle_m2m_field(instance, 'languages_spoken', add_languages_spoken, remove_languages_spoken)
        handle_m2m_field(instance, 'accepted_currencies', add_accepted_currencies, remove_accepted_currencies)
        handle_m2m_field(instance, 'available_payment_methods', add_available_payment_methods,
                         remove_available_payment_methods)

        # instance = LandlordProfile.objects.select_related('default_currency').prefetch_related(
        #     'languages_spoken', 'accepted_currencies', 'available_payment_methods'
        # ).get(pk=instance.pk)

        return instance

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        created_by: User = self.instance.created_by
        landlord_type: str = self.instance.landlord_type
        phone: str | None = attrs.get('phone', None)
        name: str | None = attrs.get('user_full_name', None)

        add_languages_spoken: List[Language] = attrs.get('add_languages_spoken', [])
        remove_languages_spoken: List[Language] = attrs.get('remove_languages_spoken', [])

        add_accepted_currencies: List[Currency] = attrs.get('add_accepted_currencies', [])
        remove_accepted_currencies: List[Currency] = attrs.get('remove_accepted_currencies', [])

        add_available_payment_methods: List[PaymentMethod] = attrs.get('add_available_payment_methods', [])
        remove_available_payment_methods: List[PaymentMethod] = attrs.get('remove_available_payment_methods', [])

        non_field_errors: List[str] = []

        result: str | None = check_m2m_conflict(add_languages_spoken, remove_languages_spoken,
                                                'languages_spoken')
        if result:
            non_field_errors.append(result)

        result: str | None = check_m2m_conflict(add_accepted_currencies, remove_accepted_currencies,
                                                'accepted_currencies')
        if result:
            non_field_errors.append(result)

        result: str | None = check_m2m_conflict(add_available_payment_methods, remove_available_payment_methods,
                                                'available_payment_methods')
        if result:
            non_field_errors.append(result)

        if phone and not match_phone_number(phone):
            non_field_errors.append(LANDLORD_PROFILE_ERRORS['phone'])

        if name and landlord_type == LandlordType.INDIVIDUAL.value[0]:
            if name != f'{created_by.first_name} {created_by.last_name}':
                non_field_errors.append(LANDLORD_PROFILE_ERRORS['user_full_name'])

        if non_field_errors:
            raise ValidationError({'non_field_errors': non_field_errors})

        return attrs


class CompanyMembershipCreateSerializer(ModelSerializer):
    email = CharField(write_only=True, required=True)
    user = UserBasePublicSerializer(read_only=True)
    role_display = CharField(source='get_role_display', read_only=True)

    class Meta:
        model = CompanyMembership
        exclude = ['user_token', 'user_full_name', 'created_at', 'updated_at', 'is_deleted', 'deleted_at']
        read_only_fields = ['company']

    def create(self, validated_data: Dict[str, Any]) -> CompanyMembership:
        validated_data['user'] = self.context['user']
        validated_data['company'] = self.context['landlord_profile']

        return super().create(validated_data)


class CompanyMembershipBasePublicSerializer(ModelSerializer):
    role = CharField(source='get_role_display', read_only=True)
    languages_spoken = LanguageSerializer(many=True, read_only=True)

    class Meta:
        model = CompanyMembership
        fields = ['id', 'user', 'user_full_name', 'company', 'role', 'languages_spoken']


class CompanyMembershipBaseSerializer(CompanyMembershipBasePublicSerializer):
    class Meta(CompanyMembershipBasePublicSerializer.Meta):
        model = CompanyMembershipBasePublicSerializer.Meta.model
        fields = CompanyMembershipBasePublicSerializer.Meta.fields + ['is_active', 'joined_at', 'left_at']


class CompanyMembershipSerializer(ModelSerializer):
    user = UserBasePublicSerializer(read_only=True)
    company_name = CharField(source='company.name', read_only=True)
    role_display = CharField(source='get_role_display', read_only=True)
    languages_spoken = LanguageSerializer(many=True, read_only=True)
    add_languages_spoken = PKLanguagesList()
    remove_languages_spoken = PKLanguagesList()

    class Meta:
        model = CompanyMembership
        exclude = ['user_token', 'user_full_name', 'is_deleted', 'deleted_at', 'created_at', 'updated_at']
        read_only_fields = ['company', 'joined_at']

    @atomic_handel
    def update(self, instance: CompanyMembership, validated_data: Dict[str, Any]) -> CompanyMembership:
        add_languages_spoken: List[Language] = validated_data.pop('add_languages_spoken', [])
        remove_languages_spoken: List[Language] = validated_data.pop('remove_languages_spoken', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if add_languages_spoken:
            instance.languages_spoken.add(*add_languages_spoken)

        if remove_languages_spoken:
            instance.languages_spoken.remove(*remove_languages_spoken)

        return instance

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        add_languages_spoken: List[Language] = attrs.get('add_languages_spoken', [])
        remove_languages_spoken: List[Language] = attrs.get('remove_languages_spoken', [])

        result: str | None = check_m2m_conflict(add_languages_spoken, remove_languages_spoken,
                                                'languages_spoken')
        if result:
            raise ValidationError({'non_field_errors': [result]})

        return attrs
