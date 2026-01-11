# Testing Guide for Celery Background Tasks

This guide explains how to test the Celery background task implementation for email notifications.

## Prerequisites

1. RabbitMQ server must be running
2. Celery worker must be running
3. Django development server must be running

## Setup Steps

### 1. Start RabbitMQ

**Option A: Using Docker (Recommended)**
```bash
docker-compose up -d rabbitmq
```

**Option B: Native Installation**
- Windows: `rabbitmq-service start` (run as Administrator)
- Linux: `sudo systemctl start rabbitmq-server`
- macOS: `brew services start rabbitmq`

Verify RabbitMQ is running:
```bash
rabbitmqctl status
```

### 2. Configure Environment

Copy `.env.example` to `.env`:
```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/macOS
```

### 3. Install Dependencies

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Start Django Server

In Terminal 1:
```bash
python manage.py runserver
```

### 6. Start Celery Worker

In Terminal 2 (with virtual environment activated):
```bash
celery -A alx_travel_app worker --loglevel=info
```

You should see output like:
```
[tasks]
  . listings.tasks.send_booking_confirmation_email
```

## Testing the Background Task

### Test 1: Create a Listing

```bash
curl -X POST http://localhost:8000/api/listings/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Beautiful Beach House",
    "description": "A stunning beachfront property",
    "location": "Miami, FL",
    "price_per_night": "250.00",
    "max_guests": 6
  }'
```

Save the `id` from the response (e.g., `1`).

### Test 2: Create a Booking (Triggers Email Task)

```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "listing": 1,
    "guest_name": "Jane Doe",
    "guest_email": "jane@example.com",
    "start_date": "2024-07-01",
    "end_date": "2024-07-05",
    "total_price": "1000.00",
    "status": "PENDING"
  }'
```

### Test 3: Verify Email Task Execution

Check the Celery worker terminal (Terminal 2). You should see:

```
[INFO] Task listings.tasks.send_booking_confirmation_email[<task-id>] received
[INFO] Task listings.tasks.send_booking_confirmation_email[<task-id>] succeeded
```

Check the Django server terminal (Terminal 1). With the console email backend (default), you should see the email content printed:

```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Booking Confirmation - ALX Travel App
From: noreply@alxtravelapp.com
To: jane@example.com
Date: ...

Dear Jane Doe,

Thank you for your booking! Your reservation has been confirmed.
...
```

### Test 4: Run Unit Tests

```bash
pytest listings/tests.py -v
```

Or using Django's test runner:
```bash
python manage.py test listings
```

## Troubleshooting

### Issue: "ConnectionRefusedError: [Errno 111] Connection refused"

**Solution**: RabbitMQ is not running. Start it using one of the methods above.

### Issue: Celery worker shows "No tasks found"

**Solution**: 
1. Make sure `listings` is in `INSTALLED_APPS` in `settings.py`
2. Restart the Celery worker
3. Check that `listings/tasks.py` exists and has the `@shared_task` decorator

### Issue: Task is not executing

**Solution**:
1. Verify the Celery worker is running and connected to RabbitMQ
2. Check Celery worker logs for errors
3. Verify `send_booking_confirmation_email.delay()` is being called in `BookingViewSet.perform_create()`

### Issue: Email not appearing

**Solution**:
1. With console backend (default), emails appear in Django server logs
2. Check that `EMAIL_BACKEND` is set to `django.core.mail.backends.console.EmailBackend` in `.env`
3. For SMTP, verify email credentials are correct

## Expected Behavior

1. When a booking is created via API, the response returns immediately
2. The email task is queued in RabbitMQ
3. The Celery worker picks up the task from the queue
4. The email is sent asynchronously (doesn't block the API response)
5. Email content appears in Django logs (console backend) or is sent via SMTP

## Monitoring

### RabbitMQ Management UI

Access the RabbitMQ management interface:
- URL: http://localhost:15672
- Username: guest
- Password: guest

View queues, messages, and connections.

### Django Admin (Task Results)

With `django-celery-results` installed, view task results at:
- URL: http://localhost:8000/admin/django_celery_results/taskresult/
