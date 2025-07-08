import os
import django
from datetime import timedelta
from django.utils import timezone

# Set Django settings module before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fit_api.settings')
django.setup()

from bookings.models import FitnessClass, Booking

# --- Data Cleanup ---
# Delete all existing bookings and classes to start fresh
Booking.objects.all().delete()
FitnessClass.objects.all().delete()

now = timezone.now()

# --- Seed Data ---

# 1. Bookable class (valid future class with available slots)
yoga = FitnessClass.objects.create(
    name="Yoga",
    instructor="Instructor-1",
    scheduled_at=now + timedelta(days=1, hours=6),
    available_slots=10
)

# 2. Class scheduled within 4 hours (should trigger "booking window closed" in tests)
FitnessClass.objects.create(
    name="Too Late",
    instructor="Instructor-2",
    scheduled_at=now + timedelta(hours=3),
    available_slots=5
)

# 3. Full class (0 slots available; booking should fail)
FitnessClass.objects.create(
    name="HIIT",
    instructor="Instructor-3",
    scheduled_at=now + timedelta(days=1, hours=2),
    available_slots=0
)

# 4. Two classes at the same time (used to test overlapping class booking prevention)
clash_time = now + timedelta(days=2)

clash1 = FitnessClass.objects.create(
    name="Zumba",
    instructor="Instructor-4",
    scheduled_at=clash_time,
    available_slots=5
)

clash2 = FitnessClass.objects.create(
    name="Pilates",
    instructor="Instructor-5",
    scheduled_at=clash_time,
    available_slots=5
)

# 5. Three classes within a 24-hour period (for testing daily booking limit enforcement)
window_base = now + timedelta(days=3)

dl1 = FitnessClass.objects.create(
    name="Strength",
    instructor="Instructor-6",
    scheduled_at=window_base + timedelta(hours=1),
    available_slots=5
)

dl2 = FitnessClass.objects.create(
    name="Cardio",
    instructor="Instructor-7",
    scheduled_at=window_base + timedelta(hours=5),
    available_slots=5
)

dl3 = FitnessClass.objects.create(
    name="Stretching",
    instructor="Instructor-8",
    scheduled_at=window_base + timedelta(hours=9),
    available_slots=5
)

print("✅ Seed data loaded successfully.")
