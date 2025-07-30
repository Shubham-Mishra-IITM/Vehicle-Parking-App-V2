#!/bin/bash

# Script to stop Celery worker and beat scheduler

echo "Stopping Celery services..."

# Stop Celery worker
if [ -f celery_worker.pid ]; then
    echo "Stopping Celery Worker..."
    kill -TERM $(cat celery_worker.pid)
    rm celery_worker.pid
    echo "Celery Worker stopped"
else
    echo "Celery Worker PID file not found"
fi

# Stop Celery beat
if [ -f celery_beat.pid ]; then
    echo "Stopping Celery Beat..."
    kill -TERM $(cat celery_beat.pid)
    rm celery_beat.pid
    echo "Celery Beat stopped"
else
    echo "Celery Beat PID file not found"
fi

# Clean up beat schedule file
if [ -f celerybeat-schedule ]; then
    rm celerybeat-schedule
    echo "Cleaned up beat schedule file"
fi

echo "All Celery services stopped successfully!"
