from django.contrib import admin
from .models import Listing, Booking, Review


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price_per_night', 'max_guests', 'created_at')
    list_filter = ('location', 'created_at')
    search_fields = ('title', 'description', 'location')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('guest_name', 'listing', 'start_date', 'end_date', 'status', 'total_price')
    list_filter = ('status', 'start_date', 'created_at')
    search_fields = ('guest_name', 'guest_email', 'listing__title')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer_name', 'listing', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('reviewer_name', 'comment', 'listing__title')
