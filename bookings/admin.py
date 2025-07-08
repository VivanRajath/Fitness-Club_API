from django.contrib import admin
from .models import FitnessClass, Booking

@admin.register(FitnessClass)
class FitnessClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'instructor', 'scheduled_at', 'available_slots')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_email', 'fitness_class', 'class_time', 'daily_bookings')

    def class_time(self, obj):
        return obj.fitness_class.scheduled_at

    def daily_bookings(self, obj):
        return Booking.objects.filter(
            client_email=obj.client_email,
            fitness_class__scheduled_at__date=obj.fitness_class.scheduled_at.date()
        ).count()
