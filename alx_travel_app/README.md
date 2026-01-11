# ALX Travel App 0x03

A Django REST Framework API for travel bookings with Celery background task management using RabbitMQ and email notifications.

## Features

- RESTful API for managing listings, bookings, and reviews
- Celery integration with RabbitMQ as message broker
- Asynchronous email notifications for booking confirmations
- Django REST Framework with Swagger/OpenAPI documentation
- Comprehensive test coverage

## Project Structure

```
alx_travel_app_0x03/
├── alx_travel_app/
│   ├── __init__.py
│   ├── celery.py          # Celery configuration
│   ├── settings.py        # Django settings with Celery config
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── listings/
│   ├── __init__.py
│   ├── models.py          # Listing, Booking, Review models
│   ├── serializers.py
│   ├── views.py           # ViewSets with async email trigger
│   ├── urls.py
│   ├── tasks.py           # Celery tasks for email notifications
│   ├── admin.py
│   └── tests.py
├── manage.py
├── requirements.txt
├── .env.example
├── .flake8
└── README.md
```

## Setup Instructions

### 1. Prerequisites

- Python 3.11+
- RabbitMQ server
- Virtual environment (recommended)

### 2. Install RabbitMQ

**Windows:**
- Download and install from [RabbitMQ Downloads](https://www.rabbitmq.com/download.html)
- Or use Chocolatey: `choco install rabbitmq`
- Start RabbitMQ service: `rabbitmq-service start` (as Administrator)

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install rabbitmq-server
sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server
```

**macOS:**
```bash
brew install rabbitmq
brew services start rabbitmq
```

Verify RabbitMQ is running:
```bash
rabbitmqctl status
```

### 3. Create Virtual Environment

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Copy `.env.example` to `.env`:
```bash
copy .env.example .env  # Windows
cp .env.example .env    # Linux/macOS
```

Edit `.env` and update the following:
- `SECRET_KEY`: Generate a new Django secret key
- `CELERY_BROKER_URL`: RabbitMQ connection URL (default: `amqp://localhost`)
- Email settings if you want to use SMTP (otherwise console backend is fine for development)

### 6. Run Migrations

```bash
python manage.py migrate
```

### 7. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 8. Start Development Server

In one terminal:
```bash
python manage.py runserver
```

### 9. Start Celery Worker

In another terminal (with virtual environment activated):
```bash
celery -A alx_travel_app worker --loglevel=info
```

### 10. Access the Application

- API Root: http://localhost:8000/api/
- Admin Panel: http://localhost:8000/admin/
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## Celery Configuration

### Celery Settings

The project is configured to use RabbitMQ as the message broker. Key settings in `settings.py`:

```python
CELERY_BROKER_URL = 'amqp://localhost'  # RabbitMQ connection URL
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'django-db'
```

### Background Tasks

The email notification task is defined in `listings/tasks.py`:

```python
@shared_task
def send_booking_confirmation_email(booking_id):
    # Sends booking confirmation email asynchronously
```

This task is automatically triggered when a booking is created via the `BookingViewSet.perform_create()` method using `.delay()`:

```python
send_booking_confirmation_email.delay(booking.id)
```

## API Endpoints

### Listings

- `GET /api/listings/` - List all listings
- `POST /api/listings/` - Create a new listing
- `GET /api/listings/{id}/` - Retrieve a specific listing
- `PUT /api/listings/{id}/` - Update a listing
- `PATCH /api/listings/{id}/` - Partially update a listing
- `DELETE /api/listings/{id}/` - Delete a listing
- `GET /api/listings/{id}/bookings/` - Get bookings for a listing

### Bookings

- `GET /api/bookings/` - List all bookings (supports `?listing_id=1` query parameter)
- `POST /api/bookings/` - Create a new booking (triggers email notification)
- `GET /api/bookings/{id}/` - Retrieve a specific booking
- `PUT /api/bookings/{id}/` - Update a booking
- `PATCH /api/bookings/{id}/` - Partially update a booking
- `DELETE /api/bookings/{id}/` - Delete a booking

### Reviews

- `GET /api/reviews/` - List all reviews
- `POST /api/reviews/` - Create a new review
- `GET /api/reviews/{id}/` - Retrieve a specific review
- `PUT /api/reviews/{id}/` - Update a review
- `PATCH /api/reviews/{id}/` - Partially update a review
- `DELETE /api/reviews/{id}/` - Delete a review

## Testing

### Run Tests

```bash
pytest
```

Or using Django's test runner:
```bash
python manage.py test
```

### Test Email Task

The email task is tested in `listings/tests.py`. With the console email backend (default), emails will be printed to the console when tests run.

## Example API Usage

### Create a Listing

```bash
curl -X POST http://localhost:8000/api/listings/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cozy Apartment in Downtown",
    "description": "Beautiful 2-bedroom apartment",
    "location": "New York, NY",
    "price_per_night": "150.00",
    "max_guests": 4
  }'
```

### Create a Booking (Triggers Email)

```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "listing": 1,
    "guest_name": "John Doe",
    "guest_email": "john@example.com",
    "start_date": "2024-06-01",
    "end_date": "2024-06-05",
    "total_price": "600.00",
    "status": "PENDING"
  }'
```

When a booking is created, the email task is triggered asynchronously. Check the Celery worker logs to see the task execution.

## Email Configuration

### Console Backend (Development - Default)

Emails are printed to the console. No additional configuration needed.

### SMTP Backend (Production)

Update `.env`:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@alxtravelapp.com
```

## Monitoring Celery Tasks

### Check Celery Worker Status

The Celery worker logs will show task execution:
```
[INFO] Task listings.tasks.send_booking_confirmation_email[task-id] received
[INFO] Task listings.tasks.send_booking_confirmation_email[task-id] succeeded
```

### Using Django Admin

With `django-celery-results`, you can view task results in the Django admin panel at `/admin/django_celery_results/taskresult/`.

## Development Workflow

1. Start RabbitMQ server
2. Start Django development server: `python manage.py runserver`
3. Start Celery worker: `celery -A alx_travel_app worker --loglevel=info`
4. Create bookings via API to trigger email tasks
5. Monitor Celery worker logs for task execution

## Troubleshooting

### RabbitMQ Connection Issues

- Verify RabbitMQ is running: `rabbitmqctl status`
- Check connection URL in `.env`: `CELERY_BROKER_URL=amqp://localhost`
- Ensure RabbitMQ service is started (Windows: `rabbitmq-service start`)

### Celery Worker Not Processing Tasks

- Ensure Celery worker is running: `celery -A alx_travel_app worker --loglevel=info`
- Check RabbitMQ connection
- Verify tasks are registered: Look for "listings.tasks.send_booking_confirmation_email" in worker startup logs

### Email Not Sending

- Check email backend configuration in `.env`
- For console backend, emails appear in Django server logs
- For SMTP, verify credentials and network connectivity
- Check Celery worker logs for task errors

## License

BSD License
