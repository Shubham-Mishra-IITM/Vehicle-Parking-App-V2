from celery import Celery
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
    
    # Configure Celery
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        beat_schedule={
            'daily-reminders': {
                'task': 'tasks.daily_reminders.send_daily_reminders',
                'schedule': 86400.0,  # 24 hours
                'options': {'queue': 'reminders'}
            },
            'monthly-reports': {
                'task': 'tasks.monthly_reports.send_monthly_reports',
                'schedule': 30 * 24 * 3600.0,  # 30 days
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
