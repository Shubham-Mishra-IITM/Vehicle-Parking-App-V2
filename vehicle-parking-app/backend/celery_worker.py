#!/usr/bin/env python3
"""
Celery worker entry point with Flask app context
"""
import os
import sys

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Change to the backend directory to ensure correct paths
os.chdir(current_dir)

from app import app
from tasks.celery_app import celery

# Import all task modules to ensure they're registered
import tasks.daily_reminders
import tasks.monthly_reports
import tasks.export_csv

# Update the ContextTask to use Flask app context
class ContextTask(celery.Task):
    """Make celery tasks work with Flask app context."""
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

if __name__ == '__main__':
    celery.start()
