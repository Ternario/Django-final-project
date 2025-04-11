from datetime import datetime, timedelta

from django.urls import reverse
from django.utils.timezone import now, make_aware

from booking_project.models import Booking, Placement
from booking_project.models.choices import CheckInTime, CheckOutTime, BookingStatus
from booking_project.tests.api.base_setup_data.users_setup_data import BaseUsersSetupData


class BookingSetup(BaseUsersSetupData):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.check_in_date1 = now().date() + timedelta(days=3)
        cls.check_in_date2 = now().date() + timedelta(days=14)
        cls.check_in_date3 = now().date() + timedelta(days=15)
        cls.check_out_date1 = now().date() + timedelta(days=13)
        cls.check_out_date2 = now().date() + timedelta(days=23)
        cls.check_out_date3 = now().date() + timedelta(days=33)

        cls.bad_cancel_date = now().date() + timedelta(days=1)

        cls.placement = Placement.objects.create(
            owner=cls.landlord_user2,
            category=cls.hotel_category,
            title="First Hotel by Landlord User2 for booking",
            description="A" * 50,
            price=250,
            number_of_rooms=2,
            placement_area=43.5,
            total_beds=3,
            single_bed=2,
            double_bed=1,
            is_active=True
        )

        cls.placement2 = Placement.objects.create(
            owner=cls.landlord_user,
            category=cls.hostel_category,
            title="First Hostel by Landlord User for booking",
            description="A" * 50 + "hostel one",
            price=150,
            number_of_rooms=3,
            placement_area=43.5,
            total_beds=3,
            single_bed=2,
            double_bed=1,
            is_active=True
        )

        cls.placement3 = Placement.objects.create(
            owner=cls.landlord_user2,
            category=cls.hotel_category,
            title="Second Hotel by Landlord User2 for booking",
            description="A" * 50,
            price=250,
            number_of_rooms=2,
            placement_area=43.5,
            total_beds=3,
            single_bed=2,
            double_bed=1,
            is_active=True
        )

        cls.booking2 = Booking.objects.create(
            placement=cls.placement2,
            user=cls.regular_user,
            check_in_date=cls.bad_cancel_date,
            check_out_date=cls.check_out_date1,
            check_in_time=CheckInTime._11AM.value,
            check_out_time=CheckOutTime._10AM.value,
            status=BookingStatus.CONFIRMED.value,
            is_active=True,
        )

        cls.booking3 = Booking.objects.create(
            placement=cls.placement,
            user=cls.landlord_user,
            check_in_date=cls.check_in_date2,
            check_out_date=cls.check_out_date2,
            check_in_time=CheckInTime._11AM.value,
            check_out_time=CheckOutTime._10AM.value,
            status=BookingStatus.CANCELLED.value,
            is_active=False,
            cancelled_by=cls.landlord_user2,
            cancellation_reason="A" * 50,
            cancelled_at=make_aware(
                datetime.combine(cls.check_in_date2, datetime.strptime('13:30', '%H:%M').time()) + timedelta(
                    days=3))
        )

        cls.booking4 = Booking.objects.create(
            placement=cls.placement,
            user=cls.landlord_user,
            check_in_date=cls.check_in_date1,
            check_out_date=cls.check_out_date1,
            check_in_time=CheckInTime._11AM.value,
            check_out_time=CheckOutTime._10AM.value,
            status=BookingStatus.COMPLETED.value,
            is_active=False,
            cancelled_by=cls.landlord_user,
            cancellation_reason="A" * 50,
            cancelled_at=make_aware(
                datetime.combine(cls.check_in_date1, datetime.strptime('15:30', '%H:%M').time()) + timedelta(
                    days=3))
        )

        cls.booking5 = Booking.objects.create(
            placement=cls.placement3,
            user=cls.landlord_user,
            check_in_date=cls.check_in_date2,
            check_out_date=cls.check_out_date2,
            check_in_time=CheckInTime._11AM.value,
            check_out_time=CheckOutTime._10AM.value,
            status=BookingStatus.CONFIRMED.value,
            is_active=True,
        )

        cls.booking_choices_url = reverse("booking-time-choices")
        cls.booking_create_url = reverse("booking-create")
        cls.booking_placement_owner_list_url = reverse("booking-placement-owner-list")
        cls.booking_owner_list_url = reverse("booking-owner-list")
        cls.booking_placement_owner_retrieve_update = lambda pk: reverse("booking-placement-owner-update",
                                                                         kwargs={"pk": pk})
        cls.booking_owner_retrieve_update = lambda pk: reverse("booking-owner-update", kwargs={"pk": pk})
        cls.inactive_booking_placement_owner_list = reverse("booking-placement-owner-inactive")
        cls.inactive_booking_owner_list = reverse("booking-owner-inactive")

    def setUp(self):
        super().setUp()

        self.booking = Booking.objects.create(
            placement=self.placement,
            user=self.landlord_user,
            check_in_date=self.check_in_date1,
            check_out_date=self.check_out_date1,
            check_in_time=CheckInTime._11AM.value,
            check_out_time=CheckOutTime._10AM.value,
            status=BookingStatus.PENDING.value,
            is_active=True,
        )
