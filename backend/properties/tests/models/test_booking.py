from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils.timezone import now

from properties.models import Booking, User

from properties.tests.models.base_models_setup import BaseModelSetupTest
from properties.utils.choices.booking import BookingStatus
from properties.utils.choices.time import CheckInTime, CheckOutTime


class BookingDetailsModelTest(BaseModelSetupTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.user = User.objects.create(
            email="user@example.com",
            first_name="User",
            last_name="User",
            username="FirstUser",
            phone="+120456789",
        )

        cls.future_start = now().date() + timedelta(days=3)
        cls.future_end = now().date() + timedelta(days=13)

        cls.booking = Booking.objects.create(
            placement=cls.placement,
            user=cls.user,
            check_in_date=cls.future_start,
            check_out_date=cls.future_end,
            check_in_time=CheckInTime._11AM.value,
            check_out_time=CheckOutTime._10AM.value,
            status=BookingStatus.PENDING.value,
            is_active=True,
        )

    def test_create_booking(self):
        """Test creating a properties."""

        self.assertIsNotNone(self.booking.id)
        self.assertIsNotNone(self.booking.placement)
        self.assertIsNotNone(self.booking.user)
        self.assertEqual(self.booking.user, self.user)
        self.assertEqual(self.booking.placement, self.placement)
        self.assertEqual(self.booking.check_in_date, self.future_start)
        self.assertEqual(self.booking.check_in_time, CheckInTime._11AM.value)
        self.assertEqual(self.booking.check_out_date, self.future_end)
        self.assertEqual(self.booking.check_out_time, CheckOutTime._10AM.value)
        self.assertEqual(self.booking.status, BookingStatus.PENDING.value)
        self.assertTrue(self.booking.is_active)
        self.assertIsNone(self.booking.cancelled_by)
        self.assertIsNone(self.booking.cancellation_reason)
        self.assertIsNone(self.booking.cancelled_at)

    def test_booking_cannot_be_created_without_required_fields(self):
        """Test the properties cannot be created without user, placement, check_in_date or check_out_date field."""

        new_booking = Booking(
            placement=None,
            user=None,
            check_in_date=None,
            check_out_date=None,
            check_in_time=CheckInTime._11AM.value,
            check_out_time=CheckOutTime._10AM.value,
            status=BookingStatus.PENDING.value,
            is_active=True,
        )

        with self.assertRaises(ValidationError) as context:
            new_booking.full_clean()
        error_message = str(context.exception)
        self.assertIn("placement", error_message)
        self.assertIn("user", error_message)
        self.assertIn("check_in_date", error_message)
        self.assertIn("check_out_date", error_message)

    def test_booking_cannot_be_created_with_past_check_in_date(self):
        """Test the properties cannot be created with check in date in the past."""

        new_booking = Booking(
            placement=self.placement,
            user=self.user,
            check_in_date=now().date() - timedelta(days=1),
            check_out_date=self.future_end,
            check_in_time=CheckInTime._11AM.value,
            check_out_time=CheckOutTime._10AM.value,
            status=BookingStatus.PENDING.value,
            is_active=True,
        )

        with self.assertRaises(ValidationError) as context:
            new_booking.full_clean()
        error_message = str(context.exception)
        self.assertIn("Start date can't be in the past.", error_message)

    def test_booking_cannot_be_created_with_date_less_than_one_day(self):
        """Test the properties cannot be created with duration less than one day."""

        new_booking = Booking(
            placement=self.placement,
            user=self.user,
            check_in_date=self.future_start,
            check_out_date=self.future_start,
            check_in_time=CheckInTime._11AM.value,
            check_out_time=CheckOutTime._10AM.value,
            status=BookingStatus.PENDING.value,
            is_active=True,
        )

        with self.assertRaises(ValidationError) as context:
            new_booking.full_clean()
        error_message = str(context.exception)
        self.assertIn("The end date must be at least one day later than the start date.", error_message)

    def test_booking_cannot_be_created_with_overlaps_dates(self):
        """Test the properties cannot be created with overlaps dates."""

        new_booking = Booking(
            placement=self.placement,
            user=self.user,
            check_in_date=self.future_start + timedelta(days=2),
            check_out_date=self.future_end + timedelta(days=3),
            check_in_time=CheckInTime._11AM.value,
            check_out_time=CheckOutTime._10AM.value,
            status=BookingStatus.PENDING.value,
            is_active=True,
        )

        with self.assertRaises(ValidationError) as context:
            new_booking.full_clean()
        error_message = str(context.exception)
        self.assertIn("This apartment is already reserved for the selected dates.", error_message)
