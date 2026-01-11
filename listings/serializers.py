"""
Serializers for the listings app.
"""
from rest_framework import serializers
from .models import Listing, Booking, Review


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for Listing model."""
    class Meta:
        model = Listing
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model."""
    class Meta:
        model = Review
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    """Serializer for Booking model."""
    listing_title = serializers.CharField(source='listing.title', read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, data):
        """Validate that end_date is after start_date."""
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError({
                'end_date': 'End date must be after start date.'
            })
        return data

    def validate_total_price(self, value):
        """Validate that total_price is non-negative."""
        if value < 0:
            raise serializers.ValidationError('Total price must be non-negative.')
        return value
