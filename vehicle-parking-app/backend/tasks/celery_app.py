from celery import Celery
from celery.schedules import crontab
from config import Config
import os

def make_celery(app_name=__name__):
    """Create and configure Celery instance"""
    celery = Celery(
        app_name,
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND,
        include=[
            'tasks.daily_reminders',
            'tasks.monthly_reports',
            'tasks.export_csv'
        ]
    )
    
    # Update task base class to include Flask app context
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            # Import here to avoid circular imports
            try:
                from app import app
                with app.app_context():
                    return self.run(*args, **kwargs)
            except ImportError:
                # Fallback for when Flask app is not available
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    
    # Configure Celery
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Kolkata',  # Indian timezone
        enable_utc=False,
        beat_schedule={
            'daily-reminders': {
                'task': 'tasks.daily_reminders.send_daily_reminders',
                'schedule': crontab(hour=18, minute=0),  # 6:00 PM IST daily
                'options': {'queue': 'reminders'}
            },
            'admin-daily-summary': {
                'task': 'tasks.daily_reminders.send_admin_daily_summary',
                'schedule': crontab(hour=19, minute=0),  # 7:00 PM IST daily
                'options': {'queue': 'reminders'}
            },
            'new-parking-lot-notifications': {
                'task': 'tasks.daily_reminders.send_new_parking_lot_notifications',
                'schedule': crontab(hour=10, minute=0),  # 10:00 AM IST daily
                'options': {'queue': 'reminders'}
            },
            'monthly-reports': {
                'task': 'tasks.monthly_reports.send_monthly_reports',
                'schedule': crontab(hour=9, minute=0, day_of_month=1),  # 1st of every month at 9 AM
                'options': {'queue': 'reports'}
            }
        },
        task_routes={
            'tasks.daily_reminders.*': {'queue': 'reminders'},
            'tasks.monthly_reports.*': {'queue': 'reports'},
            'tasks.export_csv.*': {'queue': 'exports'}
        }
    )
    
    return celery

# Create Celery instance
celery = make_celery()
