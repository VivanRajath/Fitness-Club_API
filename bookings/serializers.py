from rest_framework import serializers
from .models import FitnessClass, Booking
from django.utils import timezone
from django.db import transaction
from django.db.models import F
import pytz
from datetime import timedelta


class FitnessClassSerializer(serializers.ModelSerializer):
    """
    Serializer for the FitnessClass model.
    Maps the `scheduled_at` field to `date_time` for clearer API output.
    """
    date_time = serializers.DateTimeField(source='scheduled_at')

    class Meta:
        model = FitnessClass
        fields = ['id', 'name', 'date_time', 'instructor', 'available_slots']


class BookingSerializer(serializers.ModelSerializer):
    """
    Serializer for the Booking model.
    Includes custom validation logic to handle:
    - Class availability
    - Duplicate bookings
    - Overlapping bookings
    - Booking window restrictions
    - Booking limits within a 24-hour window
    """
    class_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'class_id', 'client_name', 'client_email']

    def validate(self, data):
        """
        Validates the incoming booking data with respect to multiple business rules.

        Raises:
            serializers.ValidationError: If any validation rule is violated.
        """
        try:
            fitness_class = FitnessClass.objects.get(id=data['class_id'])
        except FitnessClass.DoesNotExist:
            raise serializers.ValidationError({"error": "Fitness class not found."})

        # Convert current time and class time to IST
        ist = pytz.timezone('Asia/Kolkata')
        now_ist = timezone.now().astimezone(ist)
        class_time_ist = fitness_class.scheduled_at.astimezone(ist)

        # Reject bookings for classes already completed
        if class_time_ist < now_ist:
            raise serializers.ValidationError(
                {"error": "Cannot book a class scheduled in the past."}
            )

        # Booking must be made at least 4 hours before the class
        if now_ist > class_time_ist - timedelta(hours=4):
            raise serializers.ValidationError(
                {"error": "Booking window is closed. Book at least 4 hours before the class."}
            )

        email = data['client_email'].strip().lower()

        # Prevent duplicate bookings for the same class by the same email
        if Booking.objects.filter(
            fitness_class=fitness_class,
            client_email__iexact=email
        ).exists():
            raise serializers.ValidationError({"error": "You have already booked this class."})

        # Prevent booking for another class that overlaps in time
        if Booking.objects.filter(
            client_email__iexact=email,
            fitness_class__scheduled_at=fitness_class.scheduled_at
        ).exists():
            raise serializers.ValidationError({"error": "You already have a class at this time."})

        # Restrict user to a maximum of 2 bookings within a 24-hour rolling window
        window_start = class_time_ist - timedelta(hours=24)
        window_end = class_time_ist
        recent_bookings = Booking.objects.filter(
            client_email__iexact=email,
            fitness_class__scheduled_at__range=(window_start, window_end)
        )
        if recent_bookings.count() >= 2:
            raise serializers.ValidationError(
                {"error": "You can only book 2 classes within a 24-hour period."}
            )

        # Store validated context for use during creation
        self.context['fitness_class_id'] = fitness_class.id
        self.context['class_time_ist'] = class_time_ist
        self.context['client_email'] = email
        return data

    def create(self, validated_data):
        """
        Creates a new Booking instance while ensuring available slots are updated atomically.

        Returns:
            Booking: The created booking instance.
        """
        email = self.context['client_email']
        class_id = self.context['fitness_class_id']

        with transaction.atomic():
            # Lock the class row to prevent race conditions
            fitness_class = FitnessClass.objects.select_for_update().get(id=class_id)

            # Ensure there are available slots
            if fitness_class.available_slots <= 0:
                raise serializers.ValidationError({"error": "No available slots for this class."})

            # Decrement available slots
            fitness_class.available_slots = F('available_slots') - 1
            fitness_class.save(update_fields=['available_slots'])

            # Create the booking
            booking = Booking.objects.create(
                fitness_class=fitness_class,
                client_name=validated_data['client_name'],
                client_email=email
            )

        # Prepare success message with formatted time
        formatted_time = self.context['class_time_ist'].strftime('%Y-%m-%d %H:%M:%S')
        self.context['response_message'] = {
            "message": f"Booking successful for {booking.client_name} for {fitness_class.name} on {formatted_time} IST"
        }

        return booking

    def to_representation(self, instance):
        """
        Adds a custom success message to the serialized response.
        """
        response = super().to_representation(instance)
        response.update(self.context.get('response_message', {}))
        return response
