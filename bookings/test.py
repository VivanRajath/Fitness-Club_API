from django.test import TestCase
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from .models import FitnessClass, Booking


class BookingAPITestCase(TestCase):
    """
    Unit test suite for the fitness class booking API.
    """

    def setUp(self):
        """
        Set up a default fitness class scheduled for the future with one available slot.
        """
        self.client = APIClient()
        self.class_time = timezone.now() + timedelta(days=1, hours=5)

        self.fitness_class = FitnessClass.objects.create(
            name="Yoga",
            instructor="Instructor-1",
            available_slots=1,
            scheduled_at=self.class_time
        )

    def make_booking(self, class_obj, name, email):
        """
        Helper method to make a booking request.
        """
        return self.client.post('/api/book/', {
            "class_id": class_obj.id,
            "client_name": name,
            "client_email": email
        }, format='json')

    def test_successful_booking(self):
        """
        Test booking a class with valid inputs and available slot.
        """
        response = self.make_booking(self.fitness_class, "John Doe", "john@example.com")
        self.assertEqual(response.status_code, 201)
        self.assertIn("Booking successful", response.json().get("message", ""))

    def test_class_not_found(self):
        """
        Test booking a class that does not exist (invalid class_id).
        """
        response = self.client.post('/api/book/', {
            "class_id": 999,
            "client_name": "Jane",
            "client_email": "jane@example.com"
        }, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Fitness class not found", str(response.data))

    def test_no_available_slots(self):
        """
        Test booking when no slots are available.
        """
        Booking.objects.create(
            fitness_class=self.fitness_class,
            client_name="Alice",
            client_email="alice@example.com"
        )
        self.fitness_class.available_slots = 0
        self.fitness_class.save()

        response = self.make_booking(self.fitness_class, "Bob", "bob@example.com")
        self.assertEqual(response.status_code, 400)
        self.assertIn("No available slots", str(response.data))

    def test_booking_within_4_hours(self):
        """
        Test booking within 4 hours of class time — should fail.
        """
        self.fitness_class.scheduled_at = timezone.now() + timedelta(hours=3)
        self.fitness_class.available_slots = 5
        self.fitness_class.save()

        response = self.make_booking(self.fitness_class, "Late User", "late@example.com")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Booking window is closed", str(response.data))

    def test_duplicate_booking_same_class(self):
        """
        Test attempting to book the same class twice with the same email.
        """
        Booking.objects.create(
            fitness_class=self.fitness_class,
            client_name="Repeat User",
            client_email="repeat@example.com"
        )
        self.fitness_class.available_slots += 1
        self.fitness_class.save()

        response = self.make_booking(self.fitness_class, "Repeat User", "repeat@example.com")
        self.assertEqual(response.status_code, 400)
        self.assertIn("already booked this class", str(response.data))

    def test_double_booking_same_time(self):
        """
        Test booking two classes scheduled at the same time by the same user — should fail.
        """
        another_class = FitnessClass.objects.create(
            name="Zumba",
            instructor="Instructor-2",
            available_slots=5,
            scheduled_at=self.class_time
        )
        Booking.objects.create(
            fitness_class=self.fitness_class,
            client_name="Clasher",
            client_email="clash@example.com"
        )

        response = self.make_booking(another_class, "Clasher", "clash@example.com")
        self.assertEqual(response.status_code, 400)
        self.assertIn("already have a class at this time", str(response.data))

    def test_max_two_bookings_per_24_hours(self):
        """
        Test that a client cannot book more than two classes within a 24-hour window.
        """
        # First booking
        Booking.objects.create(
            fitness_class=self.fitness_class,
            client_name="Maxy",
            client_email="max@example.com"
        )

        # Second booking
        class2 = FitnessClass.objects.create(
            name="Pilates",
            instructor="Instructor-3",
            available_slots=5,
            scheduled_at=self.class_time + timedelta(hours=1)
        )
        Booking.objects.create(
            fitness_class=class2,
            client_name="Maxy",
            client_email="max@example.com"
        )

        # Third booking (should fail)
        class3 = FitnessClass.objects.create(
            name="HIIT",
            instructor="Instructor-4",
            available_slots=5,
            scheduled_at=self.class_time + timedelta(hours=2)
        )
        response = self.make_booking(class3, "Maxy", "max@example.com")
        self.assertEqual(response.status_code, 400)
        self.assertIn("24-hour", str(response.data))
