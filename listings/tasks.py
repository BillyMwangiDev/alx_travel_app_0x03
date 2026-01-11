"""
Celery tasks for the listings app.
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_booking_confirmation_email(booking_id):
    """
    Send booking confirmation email asynchronously.
    
    Args:
        booking_id: The ID of the booking to send confirmation for
    """
    from .models import Booking

    try:
        booking = Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        return f'Booking with id {booking_id} does not exist'

    subject = 'Booking Confirmation - ALX Travel App'
    message = f"""
Dear {booking.guest_name},

Thank you for your booking! Your reservation has been confirmed.

Booking Details:
- Property: {booking.listing.title}
- Location: {booking.listing.location}
- Check-in: {booking.start_date}
- Check-out: {booking.end_date}
- Total Price: ${booking.total_price}
- Status: {booking.get_status_display()}

We look forward to hosting you!

Best regards,
ALX Travel App Team
"""
    recipient_list = [booking.guest_email]
    from_email = settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=False,
        )
        return f'Booking confirmation email sent to {booking.guest_email}'
    except Exception as e:
        return f'Failed to send email: {str(e)}'
