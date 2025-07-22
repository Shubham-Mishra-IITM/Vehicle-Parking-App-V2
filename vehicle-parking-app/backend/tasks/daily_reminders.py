from celery import current_app as celery_app
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

# Optional imports - handle gracefully if not available
try:
    import requests
except ImportError:
    requests = None

@celery_app.task(bind=True)
def send_daily_reminders(self):
    """Send daily reminders to users"""
    try:
        from models.user import User
        from models.reservation import Reservation
        from database import db
        
        # Get users who haven't made a reservation in the last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        inactive_users = db.session.query(User).filter(
            User.role == 'user',
            User.is_active == True,
            ~User.id.in_(
                db.session.query(Reservation.user_id).filter(
                    Reservation.created_at >= seven_days_ago
                )
            )
        ).all()
        
        successful_sends = 0
        failed_sends = 0
        
        for user in inactive_users:
            try:
                # Send reminder via Google Chat if webhook is configured
                if Config.GOOGLE_CHAT_WEBHOOK_URL:
                    send_google_chat_reminder(user)
                
                # Send email reminder if email is configured
                if Config.MAIL_SERVER:
                    send_email_reminder(user)
                
                successful_sends += 1
                
            except Exception as e:
                print(f"Failed to send reminder to {user.username}: {str(e)}")
                failed_sends += 1
        
        return {
            'status': 'completed',
            'users_processed': len(inactive_users),
            'successful_sends': successful_sends,
            'failed_sends': failed_sends,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

def send_google_chat_reminder(user):
    """Send reminder via Google Chat webhook"""
    if not requests:
        print("Requests library not available, skipping Google Chat reminder")
        return
    
    message = {
        "text": f"🚗 Parking Reminder for {user.username}!\n\n"
                f"Hi {user.username}, we noticed you haven't booked a parking spot recently. "
                f"Don't forget to reserve your spot when you need parking!\n\n"
                f"Visit our app to book your parking spot now."
    }
    
    response = requests.post(
        Config.GOOGLE_CHAT_WEBHOOK_URL,
        json=message,
        timeout=10
    )
    
    if response.status_code != 200:
        raise Exception(f"Google Chat webhook failed: {response.status_code}")

def send_email_reminder(user):
    """Send reminder via email"""
    if not user.email:
        return
    
    subject = "🚗 Parking Reminder - Don't Forget to Book Your Spot!"
    
    html_body = f"""
    <html>
    <body>
        <h2>Hi {user.username}!</h2>
        <p>We noticed you haven't booked a parking spot recently.</p>
        <p>Don't forget to reserve your parking spot when you need it!</p>
        <p>Here are some benefits of using our parking app:</p>
        <ul>
            <li>Easy online booking</li>
            <li>Multiple parking locations</li>
            <li>Secure payment</li>
            <li>Real-time availability</li>
        </ul>
        <p><a href="http://localhost:8080" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Book Parking Now</a></p>
        <p>Best regards,<br>Parking App Team</p>
    </body>
    </html>
    """
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = Config.MAIL_DEFAULT_SENDER
    msg['To'] = user.email
    
    html_part = MIMEText(html_body, 'html')
    msg.attach(html_part)
    
    # Send email
    with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
        if Config.MAIL_USE_TLS:
            server.starttls()
        if Config.MAIL_USERNAME and Config.MAIL_PASSWORD:
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.send_message(msg)

@celery_app.task(bind=True)
def send_admin_daily_summary(self):
    """Send daily summary to admin"""
    try:
        from models.user import User
        from models.reservation import Reservation
        from models.parking_lot import ParkingLot
        from models.parking_spot import ParkingSpot
        from database import db
        
        # Get today's statistics
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        # Calculate statistics
        today_reservations = Reservation.query.filter(
            Reservation.created_at >= today_start,
            Reservation.created_at <= today_end
        ).count()
        
        active_reservations = Reservation.query.filter_by(status='active').count()
        total_revenue_today = db.session.query(
            db.func.sum(Reservation.parking_cost)
        ).filter(
            Reservation.leaving_timestamp >= today_start,
            Reservation.leaving_timestamp <= today_end,
            Reservation.status == 'completed'
        ).scalar() or 0
        
        total_spots = ParkingSpot.query.filter_by(is_active=True).count()
        occupied_spots = ParkingSpot.query.filter_by(status='O', is_active=True).count()
        
        # Get admin user
        admin = User.query.filter_by(role='admin').first()
        
        if admin and admin.email and Config.MAIL_SERVER:
            send_admin_summary_email(admin, {
                'today_reservations': today_reservations,
                'active_reservations': active_reservations,
                'total_revenue_today': float(total_revenue_today),
                'total_spots': total_spots,
                'occupied_spots': occupied_spots,
                'occupancy_rate': round((occupied_spots / total_spots) * 100, 2) if total_spots > 0 else 0
            })
        
        return {
            'status': 'completed',
            'admin_notified': admin is not None,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

def send_admin_summary_email(admin, stats):
    """Send daily summary email to admin"""
    subject = f"Daily Parking Summary - {datetime.utcnow().strftime('%Y-%m-%d')}"
    
    html_body = f"""
    <html>
    <body>
        <h2>Daily Parking Summary</h2>
        <p>Hi {admin.username},</p>
        <p>Here's your daily parking summary for {datetime.utcnow().strftime('%B %d, %Y')}:</p>
        
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #f2f2f2;">
                <th style="padding: 8px; text-align: left;">Metric</th>
                <th style="padding: 8px; text-align: left;">Value</th>
            </tr>
            <tr>
                <td style="padding: 8px;">New Reservations Today</td>
                <td style="padding: 8px;">{stats['today_reservations']}</td>
            </tr>
            <tr>
                <td style="padding: 8px;">Currently Active Reservations</td>
                <td style="padding: 8px;">{stats['active_reservations']}</td>
            </tr>
            <tr>
                <td style="padding: 8px;">Revenue Today</td>
                <td style="padding: 8px;">${stats['total_revenue_today']:.2f}</td>
            </tr>
            <tr>
                <td style="padding: 8px;">Occupied Spots</td>
                <td style="padding: 8px;">{stats['occupied_spots']} / {stats['total_spots']}</td>
            </tr>
            <tr>
                <td style="padding: 8px;">Occupancy Rate</td>
                <td style="padding: 8px;">{stats['occupancy_rate']}%</td>
            </tr>
        </table>
        
        <p>Best regards,<br>Parking App System</p>
    </body>
    </html>
    """
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = Config.MAIL_DEFAULT_SENDER
    msg['To'] = admin.email
    
    html_part = MIMEText(html_body, 'html')
    msg.attach(html_part)
    
    # Send email
    with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
        if Config.MAIL_USE_TLS:
            server.starttls()
        if Config.MAIL_USERNAME and Config.MAIL_PASSWORD:
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.send_message(msg)
