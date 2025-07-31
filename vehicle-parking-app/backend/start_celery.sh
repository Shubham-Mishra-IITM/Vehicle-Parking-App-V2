#!/bin/bash

# Script to start Celery worker and beat scheduler for the parking app

echo "Starting Celery Worker and Beat Scheduler for Parking App..."

# Ensure we're in the correct directory
cd "$(dirname "$0")"

# Set environment variables if needed
export FLASK_APP=app.py
export FLASK_ENV=development

# Start Celery worker using the Flask-integrated celery worker
echo "Starting Celery Worker with Flask app context..."
python3 -m celery -A celery_worker.celery worker --loglevel=info --detach --pidfile=celery_worker.pid --logfile=celery_worker.log --queues=celery,exports,reminders,reports

# Start Celery beat scheduler using the Flask-integrated celery worker
echo "Starting Celery Beat Scheduler with Flask app context..."
python3 -m celery -A celery_worker.celery beat --loglevel=info --detach --pidfile=celery_beat.pid --logfile=celery_beat.log

echo "Celery services started successfully!"
echo "Worker PID file: celery_worker.pid"
echo "Beat PID file: celery_beat.pid"
echo "Worker log: celery_worker.log"
echo "Beat log: celery_beat.log"
echo ""
echo "Daily reminders will be sent at 6:00 PM IST every day"
echo "Admin summaries will be sent at 9:00 PM IST every day"
echo "New parking lot notifications will be sent every 2 hours"
echo ""
echo "To stop services, run: ./stop_celery.sh"
