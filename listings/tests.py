"""
Tests for the listings app.
"""
from django.test import TestCase
from django.core import mail
from django.utils import timezone
from datetime import date, timedelta
from .models import Listing, Booking
from .tasks import send_booking_confirmation_email


class ListingModelTest(TestCase):
    """Test cases for Listing model."""
    def setUp(self):
        self.listing = Listing.objects.create(
            title='Test Apartment',
            description='A cozy apartment',
            location='New York, NY',
            price_per_night=100.00,
            max_guests=4
        )

    def test_listing_creation(self):
        """Test listing creation."""
        self.assertEqual(str(self.listing), 'Test Apartment')
        self.assertEqual(self.listing.price_per_night, 100.00)


class BookingModelTest(TestCase):
    """Test cases for Booking model."""
    def setUp(self):
        self.listing = Listing.objects.create(
            title='Test Apartment',
            description='A cozy apartment',
            location='New York, NY',
            price_per_night=100.00,
            max_guests=4
        )
        self.start_date = date.today() + timedelta(days=7)
        self.end_date = date.today() + timedelta(days=10)

    def test_booking_creation(self):
        """Test booking creation."""
        booking = Booking.objects.create(
            listing=self.listing,
            guest_name='John Doe',
            guest_email='john@example.com',
            start_date=self.start_date,
            end_date=self.end_date,
            total_price=300.00,
            status='PENDING'
        )
        self.assertEqual(str(booking), 'John Doe - Test Apartment')
        self.assertEqual(booking.status, 'PENDING')


class EmailTaskTest(TestCase):
    """Test cases for email task."""
    def setUp(self):
        self.listing = Listing.objects.create(
            title='Test Apartment',
            description='A cozy apartment',
            location='New York, NY',
            price_per_night=100.00,
            max_guests=4
        )
        self.booking = Booking.objects.create(
            listing=self.listing,
            guest_name='John Doe',
            guest_email='john@example.com',
            start_date=date.today() + timedelta(days=7),
            end_date=date.today() + timedelta(days=10),
            total_price=300.00,
            status='PENDING'
        )

    def test_send_booking_confirmation_email(self):
        """Test sending booking confirmation email."""
        # Clear mail outbox
        mail.outbox = []

        # Call the task directly (synchronously for testing)
        result = send_booking_confirmation_email(self.booking.id)

        # Check that email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Booking Confirmation - ALX Travel App')
        self.assertIn(self.booking.guest_email, mail.outbox[0].to)
