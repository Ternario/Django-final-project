from datetime import timedelta

from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.timezone import now

from properties.models import User, Booking
from properties.models.deletion_log import DeletionLog
from properties.models.review import Review
from properties.tests.models.base_models_setup import BaseModelSetupTest
from properties.utils.choices.deletion import DeletionType

from properties.utils.choices.booking import ReviewStatus, BookingStatus
from properties.utils.choices.time import CheckInTime, CheckOutTime


class ReviewModelTest(BaseModelSetupTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.admin_user = User.objects.create(
            email="adminuser@example.com",
            first_name="Admin",
            last_name="Admin",
            username="AdminUser",
            phone="+120456789",
            is_admin=True
        )

        cls.user = User.objects.create(
            email="user@example.com",
            first_name="User",
            last_name="User",
            username="FirstUser",
            phone="+987654321",
        )

        cls.check_in_date = now().date()
        cls.check_out_date = now().date() + timedelta(days=1)

        cls.first_booking = Booking.objects.create(
            placement=cls.placement,
            user=cls.user,
            check_in_date=cls.check_in_date,
            check_out_date=cls.check_out_date,
            check_in_time=CheckInTime._11AM.value,
            check_out_time=CheckOutTime._10AM.value,
            status=BookingStatus.COMPLETED.value,
            is_active=False,
        )

        cls.second_booking = Booking.objects.create(
            placement=cls.placement,
            user=cls.user,
            check_in_date=cls.check_in_date,
            check_out_date=cls.check_out_date,
            check_in_time=CheckInTime._11AM.value,
            check_out_time=CheckOutTime._10AM.value,
            status=BookingStatus.COMPLETED.value,
            is_active=False,
        )

        cls.third_booking = Booking.objects.create(
            placement=cls.placement,
            user=cls.user,
            check_in_date=cls.check_in_date,
            check_out_date=cls.check_out_date,
            check_in_time=CheckInTime._11AM.value,
            check_out_time=CheckOutTime._10AM.value,
            status=BookingStatus.COMPLETED.value,
            is_active=False,
        )

        cls.fourth_booking = Booking.objects.create(
            placement=cls.placement,
            user=cls.user,
            check_in_date=cls.check_in_date,
            check_out_date=cls.check_out_date,
            check_in_time=CheckInTime._11AM.value,
            check_out_time=CheckOutTime._10AM.value,
            status=BookingStatus.CONFIRMED.value,
            is_active=True,
        )

        cls.fifth_booking = Booking.objects.create(
            placement=cls.placement,
            user=cls.user,
            check_in_date=cls.check_in_date + timedelta(days=3),
            check_out_date=cls.check_out_date + timedelta(days=5),
            check_in_time=CheckInTime._11AM.value,
            check_out_time=CheckOutTime._10AM.value,
            status=BookingStatus.CANCELLED.value,
            is_active=False,
        )

        cls.review = Review.objects.create(
            booking=cls.first_booking,
            author=cls.user,
            placement=cls.first_booking.placement,
            rating=5,
        )

    def setUp(self):
        super().setUp()

        self.second_review = Review.objects.create(
            booking=self.second_booking,
            author=self.user,
            placement=self.second_booking.placement,
            feedback="",
            rating=5,
        )

    def test_create_review(self):
        """Test that a review is created successfully with valid data"""

        self.assertIsNotNone(self.review.id)
        self.assertIsNotNone(self.review.booking)
        self.assertIsNotNone(self.review.author)
        self.assertEqual(self.review.author, self.user)
        self.assertEqual(self.review.author_username, self.user.username)
        self.assertEqual(self.review.booking, self.first_booking)
        self.assertEqual(self.review.placement, self.first_booking.placement)
        self.assertEqual(self.review.status, ReviewStatus.PUBLISHED.value)
        self.assertEqual(self.review.feedback, "")
        self.assertEqual(self.review.rating, 5)

    def test_review_requires_booking_author_placement_rating(self):
        """Test that a  review cannot be created without a properties, author, placement or rating field."""

        new_review = Review(
            booking=None,
            author=None,
            placement=None,
            feedback="",
            rating=None,
        )

        with self.assertRaises(ValidationError) as context:
            new_review.full_clean()
        error_message = str(context.exception)
        self.assertIn("properties", error_message)
        self.assertIn("author", error_message)
        self.assertIn("placement", error_message)
        self.assertIn("rating", error_message)

    def test_review_requires_feedback_if_rating_below_5(self):
        """Test that a review cannot be created without feedback if the rating is below 5."""

        new_review = Review(
            booking=self.third_booking,
            author=self.user,
            placement=self.third_booking.placement,
            feedback="",
            rating=4,
        )

        with self.assertRaises(ValidationError) as context:
            new_review.full_clean()
        error_message = str(context.exception)
        self.assertIn("feedback_required", error_message)

    def test_fields_min_length_or_min_value(self):
        """Test the minimum length or value of the fields: feedback, rating, owner_response, moderator_notes."""

        new_review = Review(
            booking=self.third_booking,
            author=self.user,
            placement=self.third_booking.placement,
            feedback="A" * 9,
            rating=0,
            owner_response="A" * 9,
            moderator_notes="A" * 9
        )

        with self.assertRaises(ValidationError) as context:
            new_review.full_clean()
        error_message = str(context.exception)
        self.assertIn("feedback", error_message)
        self.assertIn("rating", error_message)
        self.assertIn("owner_response", error_message)
        self.assertIn("moderator_notes", error_message)

    def test_fields_max_length_or_max_value(self):
        """Test the maximum length or value of the fields: feedback, rating, owner_response and moderator_notes."""

        new_review = Review(
            booking=self.third_booking,
            author=self.user,
            placement=self.third_booking.placement,
            feedback="A" * 2001,
            rating=6,
            owner_response="A" * 1001,
            moderator_notes="A" * 2001
        )

        with self.assertRaises(ValidationError) as context:
            new_review.full_clean()
        error_message = str(context.exception)
        self.assertIn("feedback", error_message)
        self.assertIn("rating", error_message)
        self.assertIn("owner_response", error_message)
        self.assertIn("moderator_notes", error_message)

    def test_user_cannot_create_review_without_booking(self):
        """Test a user cannot create review if he has no properties."""

        new_review = Review(
            booking=self.second_booking,
            author=self.admin_user,
            placement=self.second_booking.placement,
            feedback="",
            rating=5,
        )

        with self.assertRaises(ValidationError) as context:
            new_review.full_clean()
        error_message = str(context.exception)
        self.assertIn('no_booking', error_message)

    def test_user_cannot_create_review_while_booking_is_active(self):
        """Test a user cannot create review if properties is active."""

        new_review = Review(
            booking=self.fourth_booking,
            author=self.user,
            placement=self.fourth_booking.placement,
            feedback="",
            rating=5,
        )

        with self.assertRaises(ValidationError) as context:
            new_review.full_clean()
        error_message = str(context.exception)
        self.assertIn('active_booking', error_message)

    def test_user_cannot_create_review_with_booking_cancelled_before_check_in_day(self):
        """Test that a user cannot create review if properties was cancelled before check in date"""

        new_review = Review(
            booking=self.fifth_booking,
            author=self.user,
            placement=self.fifth_booking.placement,
            feedback="",
            rating=5,
        )

        with self.assertRaises(ValidationError) as context:
            new_review.full_clean()
        error_message = str(context.exception)
        self.assertIn('cancelled_before_start', error_message)

    def test_user_cannot_create_second_review_to_the_same_booking(self):
        """Test that a user cannot duplicate review to the same properties"""

        new_review = Review(
            booking=self.first_booking,
            author=self.user,
            placement=self.first_booking.placement,
            feedback="",
            rating=5,
        )

        with self.assertRaises(ValidationError) as context:
            new_review.full_clean()
        error_message = str(context.exception)
        self.assertIn('duplicate', error_message)

    def test_admin_cannot_soft_delete_without_reason(self):
        """Test that an admin cannot perform a soft delete of a review without providing a reason."""

        with self.assertRaises(ValidationError) as context:
            self.second_review.soft_delete(user=self.admin_user, reason="")

        error_message = str(context.exception)
        self.assertIn("removed_reason", error_message)

    def test_review_author_can_soft_delete_review(self):
        """Test that the review's author can soft-delete their review."""

        self.second_review.soft_delete(self.user)

        self.assertEqual(self.second_review.status, ReviewStatus.DELETED.value)
        self.assertEqual(DeletionLog.objects.count(), 1)

        deletion_log_object = DeletionLog.objects.get(deleted_by=self.user)

        self.assertEqual(deletion_log_object.deleted_object_id, self.second_review.pk)
        self.assertEqual(deletion_log_object.deletion_type, DeletionType.SOFT_DELETE.value)

    def test_non_admin_cannot_privacy_delete(self):
        """Test that a non-admin user cannot perform privacy delete of a model."""

        with self.assertRaises(PermissionDenied) as context:
            self.second_review.privacy_delete(self.user, "A" * 100)

        error_message = str(context.exception)
        self.assertIn("permission", error_message)
        self.assertFalse(DeletionLog.objects.count())

    def test_admin_cannot_privacy_delete_without_reason_provided(self):
        """Test that an admin cannot perform a privacy delete of a model without providing a reason."""

        with self.assertRaises(ValidationError) as context:
            self.second_review.privacy_delete(user=self.admin_user, reason="")

        error_message = str(context.exception)

        self.assertIn("removed_reason", error_message)
        self.assertFalse(DeletionLog.objects.count())

    def test_admin_can_privacy_delete_review(self):
        """Test that an admin can privacy-delete a review."""

        review = self.second_review

        new_feedback = ("everything was great, cool apartments, if you have any questions or need more information, "
                        "write to my nickname FirstUser or write to the email user@example.com.")

        review.feedback = new_feedback

        review.save()

        self.second_review.privacy_delete(user=self.admin_user, reason="A" * 100)

        self.assertEqual(self.second_review.status, ReviewStatus.PRIVACY_REMOVED.value)
        self.assertEqual(self.second_review.author_username, "Deleted user")

        deletion_log_object = DeletionLog.objects.get(deleted_by=self.admin_user)

        self.assertEqual(deletion_log_object.deleted_object_id, self.second_review.pk)
        self.assertEqual(deletion_log_object.deletion_type, DeletionType.PRIVACY_DELETE.value)

        deleted_review = Review.deleted_objects.get(pk=self.second_review.pk)

        self.assertFalse(deleted_review.booking)
        self.assertFalse(deleted_review.author)
        self.assertTrue(deleted_review.author_token)
        self.assertTrue(deleted_review.booking_number)
        self.assertNotEqual(deleted_review.feedback, new_feedback)
