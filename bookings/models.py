from django.db import models
from django.utils import timezone

class FitnessClass(models.Model):
    """
    Model representing a fitness class that can be scheduled and booked.
    """
    name = models.CharField(max_length=100, help_text="Name of the fitness class.")
    scheduled_at = models.DateTimeField(default=timezone.now, help_text="Date and time the class is scheduled to run.")
    instructor = models.CharField(max_length=100, help_text="Name of the instructor for the class.")
    available_slots = models.IntegerField(help_text="Number of available slots for booking.")

    def __str__(self):
        return f"{self.name} - {self.scheduled_at}"


class Booking(models.Model):
    """
    Model representing a client's booking for a fitness class.
    """
    fitness_class = models.ForeignKey(FitnessClass, on_delete=models.CASCADE, help_text="Reference to the fitness class.")
    client_name = models.CharField(max_length=100, help_text="Name of the client making the booking.")
    client_email = models.EmailField(help_text="Email address of the client.")
    confirmed = models.BooleanField(default=True, help_text="Whether the booking is confirmed.")
    created_at = models.DateTimeField(default=timezone.now, help_text="Timestamp of when the booking was created.")

    class Meta:
        unique_together = ('fitness_class', 'client_email')
        indexes = [
            models.Index(fields=['client_email']),
            models.Index(fields=['fitness_class', 'client_email']),
            models.Index(fields=['client_email', 'fitness_class']),
        ]

    def __str__(self):
        return f"{self.client_name} - {self.fitness_class.name}"
