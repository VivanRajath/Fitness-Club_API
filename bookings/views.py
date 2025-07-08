from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import FitnessClass, Booking
from .serializers import FitnessClassSerializer, BookingSerializer


@api_view(['GET'])
def get_classes(request):
    """
    Retrieve a list of all available fitness classes.

    Method: GET  
    Returns:
        200 OK with serialized list of FitnessClass objects.
    """
    classes = FitnessClass.objects.all()
    serializer = FitnessClassSerializer(classes, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def book_class(request):
    """
    Book a fitness class for a user based on submitted data.

    Method: POST  
    Request body:
        {
            "class_id": int,
            "client_name": str,
            "client_email": str
        }

    Returns:
        201 CREATED with booking details if successful.  
        400 BAD REQUEST if validation fails.
    """
    serializer = BookingSerializer(data=request.data)
    if serializer.is_valid():
        booking = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_bookings(request):
    """
    Retrieve all bookings made by a client using their email.

    Query param:
        ?email=client@example.com

    Method: GET  
    Returns:
        200 OK with serialized list of bookings made by the client.
        If no bookings are found, returns an empty list.
    """
    email = request.query_params.get('email', '')
    bookings = Booking.objects.filter(client_email=email)
    serializer = BookingSerializer(bookings, many=True)
    return Response(serializer.data)
