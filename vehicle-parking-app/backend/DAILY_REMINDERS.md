# Daily Reminders System

This document explains the scheduled reminder system implemented for the Vehicle Parking App.

## Overview

The system sends automated daily reminders to users via multiple channels:
- **SMS** (using Twilio)
- **Email** (using SMTP)
- **Google Chat** (using webhooks)

## Features

### 1. Daily User Reminders
- **Schedule**: Every day at 6:00 PM IST
- **Target**: Users who haven't made a reservation in the last 3 days
- **Content**: Personalized reminders with new parking locations (if any)

### 2. Admin Daily Summary
- **Schedule**: Every day at 9:00 PM IST
- **Target**: Admin users
- **Content**: Daily statistics including reservations, revenue, occupancy rates

### 3. New Parking Lot Notifications
- **Schedule**: Every 2 hours
- **Target**: All active users (only when new parking lots are added)
- **Content**: Information about newly added parking locations

## Setup Instructions

### 1. Install Dependencies

```bash
pip install twilio
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure the following variables:

#### Email Configuration (Required for email notifications)
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

#### Twilio SMS Configuration (Required for SMS notifications)
```env
TWILIO_ACCOUNT_SID=your-twilio-account-sid
TWILIO_AUTH_TOKEN=your-twilio-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

#### Google Chat Configuration (Optional for Google Chat notifications)
```env
GOOGLE_CHAT_WEBHOOK_URL=https://chat.googleapis.com/v1/spaces/YOUR_SPACE/messages?key=YOUR_KEY&token=YOUR_TOKEN
```

### 3. Start Redis Server

```bash
redis-server
```

### 4. Start Celery Services

```bash
# Make scripts executable (first time only)
chmod +x start_celery.sh stop_celery.sh

# Start Celery worker and beat scheduler
./start_celery.sh
```

### 5. Stop Celery Services

```bash
./stop_celery.sh
```

## Service Configuration Details

### Twilio SMS Setup
1. Create a Twilio account at https://www.twilio.com/
2. Get your account SID and auth token from the dashboard
3. Purchase a phone number for sending SMS
4. Add the credentials to your `.env` file

### Gmail SMTP Setup
1. Enable 2-factor authentication on your Gmail account
2. Generate an app password (not your regular password)
3. Use the app password in the `MAIL_PASSWORD` field

### Google Chat Webhook Setup
1. Open Google Chat
2. Go to the space where you want to receive notifications
3. Click on the space name → Apps & integrations → Incoming webhooks
4. Create a new webhook and copy the URL

## Testing the System

### Manual Testing via API

Use the following admin endpoints to test the system:

```bash
# Test daily reminders
curl -X POST http://localhost:5000/admin/test-reminders \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Test new parking lot notifications
curl -X POST http://localhost:5000/admin/test-new-lot-notifications \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Test admin daily summary
curl -X POST http://localhost:5000/admin/test-admin-summary \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Check task status
curl -X GET http://localhost:5000/admin/task-status/TASK_ID \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## Schedule Configuration

The schedules are configured in `tasks/celery_app.py`:

```python
beat_schedule={
    # Daily reminders at 6:00 PM IST
    'daily-user-reminders': {
        'task': 'tasks.daily_reminders.send_daily_reminders',
        'schedule': crontab(hour=18, minute=0),
        'options': {'queue': 'reminders'}
    },
    # Admin summary at 9:00 PM IST
    'admin-daily-summary': {
        'task': 'tasks.daily_reminders.send_admin_daily_summary',
        'schedule': crontab(hour=21, minute=0),
        'options': {'queue': 'reports'}
    },
    # New parking lot notifications every 2 hours
    'new-parking-lot-notifications': {
        'task': 'tasks.daily_reminders.send_new_parking_lot_notifications',
        'schedule': crontab(minute=0, hour='*/2'),
        'options': {'queue': 'notifications'}
    }
}
```

## Message Templates

### SMS Template
```
🚗 Hi [Name]!

We noticed you haven't booked a parking spot recently.

🆕 NEW PARKING LOCATIONS AVAILABLE:
• Location Name - ₹50/hr
• Another Location - ₹75/hr

Don't forget to reserve your parking spot when you need it!

Book now: http://localhost:8080

- Parking App Team
```

### Email Template
Professional HTML email with:
- Personalized greeting
- New parking locations (if any)
- Benefits of using the app
- Call-to-action button
- Unsubscribe information

### Google Chat Template
```
🚗 *Parking Reminder for [Name]!*

Hi [username], we noticed you haven't booked a parking spot recently. Don't forget to reserve your spot when you need parking!

*🆕 NEW PARKING LOCATIONS AVAILABLE:*
• *Location Name* - ₹50/hr (10 spots)
• *Another Location* - ₹75/hr (5 spots)

Visit our app to book your parking spot now: http://localhost:8080
```

## Monitoring and Logs

### Log Files
- Worker log: `celery_worker.log`
- Beat scheduler log: `celery_beat.log`

### Monitoring Tasks
```bash
# Monitor Celery worker
celery -A tasks.celery_app events

# Check active tasks
celery -A tasks.celery_app inspect active

# Check scheduled tasks
celery -A tasks.celery_app inspect scheduled
```

## Troubleshooting

### Common Issues

1. **Tasks not executing**
   - Check if Redis is running
   - Verify Celery worker and beat are started
   - Check log files for errors

2. **SMS not sending**
   - Verify Twilio credentials
   - Check phone number format (+91xxxxxxxxxx)
   - Ensure sufficient Twilio balance

3. **Emails not sending**
   - Verify SMTP settings
   - Check if app password is used (for Gmail)
   - Verify email format

4. **Google Chat not working**
   - Check webhook URL format
   - Verify space permissions
   - Test webhook URL manually

### Debug Commands

```bash
# Test Celery connection
python -c "from tasks.celery_app import celery; print(celery.control.ping())"

# Test email configuration
python -c "
import smtplib
from config import Config
server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
server.starttls()
server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
print('Email configuration working')
server.quit()
"

# Test Twilio configuration
python -c "
from twilio.rest import Client
from config import Config
client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
print('Twilio configuration working')
"
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` file to version control
2. **API Keys**: Rotate Twilio and email credentials regularly
3. **Webhook URLs**: Keep Google Chat webhook URLs private
4. **Rate Limiting**: Be mindful of SMS costs and email sending limits

## Cost Considerations

1. **Twilio SMS**: ~$0.0075 per SMS (varies by country)
2. **Email**: Usually free for reasonable volumes (Gmail: 500/day)
3. **Google Chat**: Free
4. **Redis**: Free for basic usage

## Future Enhancements

1. **User Preferences**: Allow users to choose notification methods
2. **Frequency Settings**: Let users set reminder frequency
3. **Template Customization**: Admin configurable message templates
4. **Analytics**: Track notification delivery rates and user engagement
5. **Push Notifications**: Add mobile push notifications
6. **WhatsApp**: Integrate WhatsApp Business API
