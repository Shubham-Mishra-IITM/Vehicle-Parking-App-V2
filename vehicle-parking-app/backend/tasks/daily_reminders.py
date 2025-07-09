from celery import shared_task
from datetime import datetime
import requests
from backend.models import User
from backend import db

@shared_task
def send_daily_reminders():
    users = User.query.all()
    for user in users:
        # Logic to check if the user has not visited recently
        # This could be based on a last_visited timestamp or similar
        if user.should_receive_reminder():
            message = f"Hello {user.username}, don't forget to book your parking spot!"
            send_message_to_chat(user.chat_id, message)

def send_message_to_chat(chat_id, message):
    webhook_url = "YOUR_GOOGLE_CHAT_WEBHOOK_URL"
    payload = {
        "text": message
    }
    requests.post(webhook_url, json=payload)