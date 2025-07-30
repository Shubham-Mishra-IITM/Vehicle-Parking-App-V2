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

try:
    from twilio.rest import Client as TwilioClient
except ImportError:
    TwilioClient = None

def _send_daily_reminders_impl():
    """Implementation of daily reminders logic"""
    try:
        from models.user import User
        from models.reservation import Reservation
        from models.parking_lot import ParkingLot
        from database import db
        
        # Get users who haven't made a reservation in the last 3 days
        three_days_ago = datetime.utcnow() - timedelta(days=3)
        
        # Get users who haven't visited (no reservations) or haven't visited recently
        inactive_users = db.session.query(User).filter(
            User.role == 'user',
            User.is_active == True,
            db.or_(
                # Users with no reservations at all
                ~User.id.in_(
                    db.session.query(Reservation.user_id).distinct()
                ),
                # Users with no recent reservations (last 3 days)
                ~User.id.in_(
                    db.session.query(Reservation.user_id).filter(
                        Reservation.created_at >= three_days_ago
                    )
                )
            )
        ).all()
        
        # Check if new parking lots were created in the last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        new_parking_lots = ParkingLot.query.filter(
            ParkingLot.created_at >= yesterday
        ).all()
        
        successful_sends = 0
        failed_sends = 0
        
        for user in inactive_users:
            try:
                # Send reminder via SMS if configured and user has phone number
                if Config.TWILIO_ACCOUNT_SID and user.phone_number:
                    send_sms_reminder(user, new_parking_lots)
                
                # Send reminder via Google Chat if webhook is configured
                if Config.GOOGLE_CHAT_WEBHOOK_URL:
                    send_google_chat_reminder(user, new_parking_lots)
                
                # Send email reminder if email is configured
                if Config.MAIL_SERVER and user.email:
                    send_email_reminder(user, new_parking_lots)
                
                # Update user's last reminder sent timestamp if we add this field later
                successful_sends += 1
                
            except Exception as e:
                print(f"Failed to send reminder to {user.username}: {str(e)}")
                failed_sends += 1
        
        return {
            'status': 'completed',
            'users_processed': len(inactive_users),
            'successful_sends': successful_sends,
            'failed_sends': failed_sends,
            'new_parking_lots': len(new_parking_lots),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

@celery_app.task(bind=True)
def send_daily_reminders(self):
    """Send daily reminders to users (Celery task)"""
    return _send_daily_reminders_impl()

def send_daily_reminders_sync():
    """Send daily reminders to users (direct call)"""
    return _send_daily_reminders_impl()

def send_sms_reminder(user, new_parking_lots=None):
    """Send reminder via SMS using Twilio"""
    if not TwilioClient:
        print("Twilio library not available, skipping SMS reminder")
        return
    
    if not user.phone_number:
        print(f"No phone number for user {user.username}, skipping SMS")
        return
    
    # Create personalized message
    message_parts = [
        f"🚗 Hi {user.full_name or user.username}!",
        "",
        "We noticed you haven't booked a parking spot recently."
    ]
    
    if new_parking_lots:
        message_parts.extend([
            "",
            "🆕 NEW PARKING LOCATIONS AVAILABLE:",
        ])
        for lot in new_parking_lots[:3]:  # Limit to 3 locations to keep SMS short
            message_parts.append(f"• {lot.prime_location_name} - ₹{lot.price}/hr")
    
    message_parts.extend([
        "",
        "Don't forget to reserve your parking spot when you need it!",
        "",
        "Book now: http://localhost:8080",
        "",
        "- Parking App Team"
    ])
    
    message_text = "\n".join(message_parts)
    
    try:
        client = TwilioClient(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        
        # Ensure phone number is in international format
        phone = user.phone_number
        if not phone.startswith('+'):
            # Assume Indian number if no country code
            phone = '+91' + phone.lstrip('0')
        
        message = client.messages.create(
            body=message_text,
            from_=Config.TWILIO_PHONE_NUMBER,
            to=phone
        )
        
        print(f"SMS sent to {user.username}: {message.sid}")
        
    except Exception as e:
        raise Exception(f"SMS sending failed: {str(e)}")

def send_google_chat_reminder(user, new_parking_lots=None):
    """Send reminder via Google Chat webhook"""
    if not requests:
        print("Requests library not available, skipping Google Chat reminder")
        return
    
    # Create message with new parking lots info if available
    message_text = f"🚗 *Parking Reminder for {user.full_name or user.username}!*\n\n"
    message_text += f"Hi {user.username}, we noticed you haven't booked a parking spot recently. "
    message_text += f"Don't forget to reserve your spot when you need parking!\n\n"
    
    if new_parking_lots:
        message_text += "*🆕 NEW PARKING LOCATIONS AVAILABLE:*\n"
        for lot in new_parking_lots:
            available_spots = lot.get_available_spots_count() if hasattr(lot, 'get_available_spots_count') else 'Available'
            message_text += f"• *{lot.prime_location_name}* - ₹{lot.price}/hr ({available_spots} spots)\n"
        message_text += "\n"
    
    message_text += "Visit our app to book your parking spot now: http://localhost:8080"
    
    message = {
        "text": message_text
    }
    
    response = requests.post(
        Config.GOOGLE_CHAT_WEBHOOK_URL,
        json=message,
        timeout=10
    )
    
    if response.status_code != 200:
        raise Exception(f"Google Chat webhook failed: {response.status_code}")

def send_email_reminder(user, new_parking_lots=None, dry_run=False):
    """Send reminder via email"""
    if not user.email:
        return False
    
    # Return early if email configuration is not set up
    if not Config.MAIL_SERVER or not Config.MAIL_USERNAME:
        if dry_run:
            print(f"✅ Email would be sent to {user.email} (Email server not configured)")
            return True
        return False
    
    if dry_run:
        print(f"✅ Email would be sent to {user.email} (Subject: Parking Reminder)")
        return True
    
    subject = "🚗 Parking Reminder - Don't Forget to Book Your Spot!"
    
    # Build new locations section if available
    new_locations_html = ""
    if new_parking_lots:
        new_locations_html = """
        <div style="background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 15px 0;">
            <h3 style="color: #28a745; margin-top: 0;">🆕 NEW PARKING LOCATIONS!</h3>
            <p>We've added new parking locations that might interest you:</p>
            <ul>"""
        
        for lot in new_parking_lots:
            available_spots = lot.get_available_spots_count() if hasattr(lot, 'get_available_spots_count') else 'Available'
            new_locations_html += f"""
                <li><strong>{lot.prime_location_name}</strong> - ₹{lot.price}/hour ({available_spots} spots available)</li>"""
        
        new_locations_html += """
            </ul>
        </div>"""
    
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #007bff;">🚗 Parking Reminder</h1>
            </div>
            
            <h2>Hi {user.full_name or user.username}!</h2>
            <p>We noticed you haven't booked a parking spot recently.</p>
            <p>Don't forget to reserve your parking spot when you need it!</p>
            
            {new_locations_html}
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #007bff; margin-top: 0;">Why Choose Our Parking App?</h3>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>🎯 Easy online booking in seconds</li>
                    <li>📍 Multiple convenient parking locations</li>
                    <li>💳 Secure and seamless payment</li>
                    <li>⏰ Real-time availability updates</li>
                    <li>📱 Mobile-friendly interface</li>
                    <li>💰 Competitive hourly rates</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:8080" 
                   style="background-color: #007bff; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold; display: inline-block;">
                   🚗 Book Parking Now
                </a>
            </div>
            
            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d;">
                <p>Best regards,<br><strong>Parking App Team</strong></p>
                <p style="font-size: 12px;">
                    You received this email because you have an account with our parking service.<br>
                    If you no longer wish to receive these reminders, please contact support.
                </p>
            </div>
        </div>
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
                <td style="padding: 8px;">₹{stats['total_revenue_today']:.2f}</td>
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

@celery_app.task(bind=True)
def send_new_parking_lot_notifications(self):
    """Send notifications to all users when new parking lots are added"""
    try:
        from models.user import User
        from models.parking_lot import ParkingLot
        from database import db
        
        # Get parking lots created in the last 24 hours
        yesterday = datetime.utcnow() - timedelta(days=1)
        new_parking_lots = ParkingLot.query.filter(
            ParkingLot.created_at >= yesterday
        ).all()
        
        if not new_parking_lots:
            return {
                'status': 'completed',
                'message': 'No new parking lots to notify about',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Get all active users
        active_users = User.query.filter_by(role='user', is_active=True).all()
        
        successful_sends = 0
        failed_sends = 0
        
        for user in active_users:
            try:
                # Send notification via SMS if configured and user has phone number
                if Config.TWILIO_ACCOUNT_SID and user.phone_number:
                    send_new_lot_sms(user, new_parking_lots)
                
                # Send notification via Google Chat if webhook is configured
                if Config.GOOGLE_CHAT_WEBHOOK_URL:
                    send_new_lot_google_chat(user, new_parking_lots)
                
                # Send email notification if email is configured
                if Config.MAIL_SERVER and user.email:
                    send_new_lot_email(user, new_parking_lots)
                
                successful_sends += 1
                
            except Exception as e:
                print(f"Failed to send new lot notification to {user.username}: {str(e)}")
                failed_sends += 1
        
        return {
            'status': 'completed',
            'users_notified': len(active_users),
            'successful_sends': successful_sends,
            'failed_sends': failed_sends,
            'new_parking_lots': len(new_parking_lots),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

def send_new_lot_sms(user, new_parking_lots):
    """Send new parking lot notification via SMS"""
    if not TwilioClient or not user.phone_number:
        return
    
    message_parts = [
        f"🚗 Hi {user.full_name or user.username}!",
        "",
        "🆕 NEW PARKING LOCATIONS AVAILABLE!",
        ""
    ]
    
    for lot in new_parking_lots[:2]:  # Limit to 2 locations for SMS
        message_parts.append(f"📍 {lot.prime_location_name}")
        message_parts.append(f"   ₹{lot.price}/hr")
        message_parts.append("")
    
    message_parts.extend([
        "Book now: http://localhost:8080",
        "",
        "- Parking App Team"
    ])
    
    message_text = "\n".join(message_parts)
    
    try:
        client = TwilioClient(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
        
        phone = user.phone_number
        if not phone.startswith('+'):
            phone = '+91' + phone.lstrip('0')
        
        client.messages.create(
            body=message_text,
            from_=Config.TWILIO_PHONE_NUMBER,
            to=phone
        )
        
    except Exception as e:
        raise Exception(f"SMS sending failed: {str(e)}")

def send_new_lot_google_chat(user, new_parking_lots):
    """Send new parking lot notification via Google Chat"""
    if not requests:
        return
    
    message_text = f"🚗 *New Parking Locations Available!*\n\n"
    message_text += f"Hi {user.username}, great news! We've added new parking locations:\n\n"
    
    for lot in new_parking_lots:
        available_spots = lot.get_available_spots_count() if hasattr(lot, 'get_available_spots_count') else 'Available'
        message_text += f"📍 *{lot.prime_location_name}*\n"
        message_text += f"   • ₹{lot.price}/hour\n"
        message_text += f"   • {available_spots} spots available\n\n"
    
    message_text += "Book your spot now: http://localhost:8080"
    
    message = {"text": message_text}
    
    requests.post(Config.GOOGLE_CHAT_WEBHOOK_URL, json=message, timeout=10)

def send_new_lot_email(user, new_parking_lots):
    """Send new parking lot notification via email"""
    if not user.email:
        return
    
    subject = "🆕 New Parking Locations Available!"
    
    locations_html = ""
    for lot in new_parking_lots:
        available_spots = lot.get_available_spots_count() if hasattr(lot, 'get_available_spots_count') else 'Available'
        locations_html += f"""
        <div style="border: 2px solid #28a745; border-radius: 8px; padding: 15px; margin: 10px 0; background-color: #f8fff8;">
            <h3 style="color: #28a745; margin-top: 0;">📍 {lot.prime_location_name}</h3>
            <p style="margin: 5px 0;"><strong>Rate:</strong> ₹{lot.price}/hour</p>
            <p style="margin: 5px 0;"><strong>Availability:</strong> {available_spots} spots available</p>
        </div>"""
    
    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #28a745;">🆕 New Parking Locations!</h1>
            </div>
            
            <h2>Hi {user.full_name or user.username}!</h2>
            <p>Great news! We've added new parking locations to serve you better:</p>
            
            {locations_html}
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:8080" 
                   style="background-color: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold; display: inline-block;">
                   🚗 Book Now
                </a>
            </div>
            
            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d;">
                <p>Best regards,<br><strong>Parking App Team</strong></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = Config.MAIL_DEFAULT_SENDER
    msg['To'] = user.email
    
    html_part = MIMEText(html_body, 'html')
    msg.attach(html_part)
    
    with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
        if Config.MAIL_USE_TLS:
            server.starttls()
        if Config.MAIL_USERNAME and Config.MAIL_PASSWORD:
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.send_message(msg)
