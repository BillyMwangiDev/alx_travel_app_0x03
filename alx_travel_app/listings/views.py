"""
Views for the listings app.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from listings.models import Listing, Booking, Review
from listings.serializers import ListingSerializer, BookingSerializer, ReviewSerializer
from listings.tasks import send_booking_confirmation_email


class ListingViewSet(viewsets.ModelViewSet):
    """ViewSet for Listing model."""
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

    @action(detail=True, methods=['get'])
    def bookings(self, request, pk=None):
        """Get all bookings for a specific listing."""
        listing = self.get_object()
        bookings = listing.bookings.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """ViewSet for Booking model."""
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get_queryset(self):
        """Filter bookings by listing_id if provided."""
        queryset = super().get_queryset()
        listing_id = self.request.query_params.get('listing_id', None)
        if listing_id is not None:
            queryset = queryset.filter(listing_id=listing_id)
        return queryset

    def perform_create(self, serializer):
        """Create booking and trigger email task."""
        booking = serializer.save()
        # Trigger email task asynchronously
        send_booking_confirmation_email.delay(booking.id)


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for Review model."""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
