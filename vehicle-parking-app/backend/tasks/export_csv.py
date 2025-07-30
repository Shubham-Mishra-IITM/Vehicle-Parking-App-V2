from celery import current_app as celery_app
from datetime import datetime, timedelta
import csv
import io
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from config import Config

@celery_app.task(bind=True)
def generate_user_csv_export(self, user_id):
    """Generate CSV export of user's parking history"""
    try:
        from models.user import User
        from models.reservation import Reservation
        from models.parking_spot import ParkingSpot
        from models.parking_lot import ParkingLot
        from database import db
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Fetching user data...', 'current': 10, 'total': 100}
        )
        
        # Get user
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Fetching reservations...', 'current': 30, 'total': 100}
        )
        
        # Get all user's reservations
        reservations = Reservation.query.filter_by(user_id=user_id).order_by(
            Reservation.created_at.desc()
        ).all()
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Generating CSV...', 'current': 60, 'total': 100}
        )
        
        # Create CSV data
        csv_data = generate_csv_data(reservations)
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Saving file...', 'current': 80, 'total': 100}
        )
        
        # Save CSV file
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"parking_history_{user.username}_{timestamp}.csv"
        
        # Create exports directory if it doesn't exist
        exports_dir = os.path.join(os.path.dirname(__file__), '..', 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        
        file_path = os.path.join(exports_dir, filename)
        
        # Write CSV file
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvfile.write(csv_data)
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Sending notification...', 'current': 90, 'total': 100}
        )
        
        # Send email notification with CSV attachment
        if user.email and Config.MAIL_SERVER:
            send_csv_export_email(user, file_path, filename)
        
        # Clean up old files (optional)
        cleanup_old_exports(exports_dir, days_to_keep=7)
        
        return {
            'status': 'Export completed successfully',
            'file_path': file_path,
            'filename': filename,
            'download_url': f'/api/user/download-csv/{filename}',
            'records_count': len(reservations),
            'generated_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

def generate_csv_data(reservations):
    """Generate comprehensive CSV data from reservations with detailed parking information"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header - Enhanced format with requested fields
    headers = [
        'Reservation ID',
        'Slot ID (Lot ID)',
        'Spot ID',
        'Spot Number',
        'Parking Lot Name',
        'Location Address',
        'Vehicle Number',
        'Created Date',
        'Created Time',
        'Parking Timestamp',
        'Leaving Timestamp',
        'Duration (Hours)',
        'Cost (Rs.)',
        'Hourly Rate (Rs.)',
        'Status',
        'Remarks',
        'Payment Status',
        'Booking Type'
    ]
    writer.writerow(headers)
    
    # Write data rows with comprehensive information
    for reservation in reservations:
        from models.parking_spot import ParkingSpot
        from models.parking_lot import ParkingLot
        
        # Get parking spot and lot information
        spot = ParkingSpot.query.get(reservation.spot_id)
        lot = ParkingLot.query.get(spot.lot_id) if spot else None
        
        # Format timestamps with full ISO format
        created_datetime = reservation.created_at.strftime('%Y-%m-%d %H:%M:%S') if reservation.created_at else ''
        created_date = reservation.created_at.strftime('%Y-%m-%d') if reservation.created_at else ''
        created_time = reservation.created_at.strftime('%H:%M:%S') if reservation.created_at else ''
        
        parking_timestamp = reservation.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S') if reservation.parking_timestamp else ''
        leaving_timestamp = reservation.leaving_timestamp.strftime('%Y-%m-%d %H:%M:%S') if reservation.leaving_timestamp else ''
        
        # Determine payment status based on reservation status
        payment_status = 'Paid' if reservation.status == 'completed' else 'Pending' if reservation.status == 'active' else 'Cancelled'
        
        # Determine booking type
        booking_type = 'Online Booking'  # Since all bookings are through the app
        
        row = [
            reservation.id,
            spot.lot_id if spot else 'N/A',
            reservation.spot_id,
            spot.spot_number if spot else 'N/A',
            lot.prime_location_name if lot else 'Unknown Location',
            lot.address if lot else 'Unknown Address',
            reservation.vehicle_number or 'N/A',
            created_date,
            created_time,
            parking_timestamp,
            leaving_timestamp,
            float(reservation.total_hours) if reservation.total_hours else 0.0,
            float(reservation.parking_cost) if reservation.parking_cost else 0.0,
            float(lot.price) if lot else 0.0,
            reservation.status.title(),
            reservation.remarks or '',
            payment_status,
            booking_type
        ]
        writer.writerow(row)
    
    return output.getvalue()

def send_csv_export_email(user, file_path, filename):
    """Send email with CSV export attachment and detailed information"""
    subject = "🚗 Your Parking History Export is Ready!"
    
    # Get file stats
    file_size = os.path.getsize(file_path) / 1024  # Size in KB
    
    # Create enhanced email body
    body = f"""
    Hi {user.username},

    Great news! Your complete parking history export has been generated successfully! 📊

    📁 Export Details:
    • File Name: {filename}
    • File Size: {file_size:.1f} KB
    • Generated: {datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')}

    📋 The CSV file contains comprehensive information about all your parking sessions:
    
    ✅ Basic Information:
    • Reservation ID and booking details
    • Slot ID (Lot ID) and Spot ID
    • Parking lot names and addresses
    • Vehicle numbers used
    
    ⏰ Timing Information:
    • Booking creation timestamps
    • Parking start and end times
    • Duration of each parking session
    
    💰 Financial Information:
    • Parking costs in Rs.
    • Hourly rates for each location
    • Payment status for each booking
    
    📍 Location & Status Details:
    • Parking spot numbers
    • Exact location addresses
    • Booking status (Completed/Active/Cancelled)
    • Any remarks or notes
    
    💡 This export includes your entire parking history till date and can be used for:
    • Personal expense tracking
    • Tax records and documentation
    • Analysis of your parking patterns
    • Backup of your parking data

    The CSV file is attached to this email and can be opened with Excel, Google Sheets, or any spreadsheet application.

    If you have any questions about your parking data or need assistance, please don't hesitate to contact our support team.

    Thank you for using our parking service! 🅿️

    Best regards,
    Parking App Team
    📧 support@parkingapp.com
    """
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = Config.MAIL_DEFAULT_SENDER
    msg['To'] = user.email
    msg['Subject'] = subject
    
    # Add body to email
    msg.attach(MIMEText(body, 'plain'))
    
    # Add CSV file as attachment with proper MIME type
    with open(file_path, 'rb') as attachment:
        part = MIMEBase('text', 'csv')  # Better MIME type for CSV files
        part.set_payload(attachment.read())
    
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        f'attachment; filename="{filename}"'  # Proper filename quoting
    )
    msg.attach(part)
    
    # Send email
    try:
        # Handle MailHog vs real SMTP servers differently
        if Config.MAIL_SERVER == 'localhost' or Config.MAIL_PORT == 1025:
            # MailHog - simple connection without TLS
            server = smtplib.SMTP()
            server.connect(Config.MAIL_SERVER or 'localhost', Config.MAIL_PORT or 1025)
            server.send_message(msg)
            server.quit()
        else:
            # Real SMTP server - use TLS and authentication
            with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
                if Config.MAIL_USE_TLS:
                    server.starttls()
                if Config.MAIL_USERNAME and Config.MAIL_PASSWORD:
                    server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
                server.send_message(msg)
    except Exception as e:
        print(f"Email sending error: {e}")
        # Don't fail the entire task if email fails
        pass

def cleanup_old_exports(exports_dir, days_to_keep=7):
    """Clean up old export files"""
    try:
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(days=days_to_keep)
        
        for filename in os.listdir(exports_dir):
            file_path = os.path.join(exports_dir, filename)
            if os.path.isfile(file_path):
                file_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_modified_time < cutoff_time:
                    os.remove(file_path)
                    print(f"Deleted old export file: {filename}")
    
    except Exception as e:
        print(f"Error cleaning up old exports: {str(e)}")

@celery_app.task(bind=True)
def generate_admin_csv_export(self, filters=None):
    """Generate CSV export of all reservations for admin"""
    try:
        from models.reservation import Reservation
        from models.parking_spot import ParkingSpot
        from models.parking_lot import ParkingLot
        from models.user import User
        from database import db
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Fetching reservations...', 'current': 20, 'total': 100}
        )
        
        # Build query based on filters
        query = Reservation.query
        
        if filters:
            if filters.get('start_date'):
                start_date = datetime.strptime(filters['start_date'], '%Y-%m-%d')
                query = query.filter(Reservation.created_at >= start_date)
            
            if filters.get('end_date'):
                end_date = datetime.strptime(filters['end_date'], '%Y-%m-%d')
                query = query.filter(Reservation.created_at <= end_date)
            
            if filters.get('status'):
                query = query.filter(Reservation.status == filters['status'])
        
        reservations = query.order_by(Reservation.created_at.desc()).all()
        
        # Update task state
        self.update_state(
            state='PROGRESS',
            meta={'status': 'Generating CSV...', 'current': 60, 'total': 100}
        )
        
        # Generate CSV with additional admin fields
        csv_data = generate_admin_csv_data(reservations)
        
        # Save file
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"admin_reservations_export_{timestamp}.csv"
        
        exports_dir = os.path.join(os.path.dirname(__file__), '..', 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        
        file_path = os.path.join(exports_dir, filename)
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvfile.write(csv_data)
        
        return {
            'status': 'Export completed successfully',
            'file_path': file_path,
            'filename': filename,
            'download_url': f'/api/admin/download-csv/{filename}',
            'records_count': len(reservations),
            'generated_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

def generate_admin_csv_data(reservations):
    """Generate CSV data with admin fields"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header with admin fields
    headers = [
        'Reservation ID',
        'User ID',
        'Username',
        'User Email',
        'Parking Lot',
        'Parking Spot',
        'Vehicle Number',
        'Parking Timestamp',
        'Leaving Timestamp',
        'Duration (Hours)',
        'Cost ($)',
        'Status',
        'Remarks',
        'Location Address',
        'Lot Price per Hour',
        'Created At',
        'Updated At'
    ]
    writer.writerow(headers)
    
    # Write data rows
    for reservation in reservations:
        from models.parking_spot import ParkingSpot
        from models.parking_lot import ParkingLot
        from models.user import User
        
        # Get related data
        user = User.query.get(reservation.user_id)
        spot = ParkingSpot.query.get(reservation.spot_id)
        lot = ParkingLot.query.get(spot.lot_id) if spot else None
        
        row = [
            reservation.id,
            reservation.user_id,
            user.username if user else 'Unknown',
            user.email if user else 'Unknown',
            lot.prime_location_name if lot else 'Unknown',
            spot.spot_number if spot else 'Unknown',
            reservation.vehicle_number,
            reservation.parking_timestamp.isoformat() if reservation.parking_timestamp else '',
            reservation.leaving_timestamp.isoformat() if reservation.leaving_timestamp else '',
            float(reservation.total_hours) if reservation.total_hours else '',
            float(reservation.parking_cost) if reservation.parking_cost else '',
            reservation.status,
            reservation.remarks or '',
            lot.address if lot else '',
            float(lot.price) if lot else '',
            reservation.created_at.isoformat() if reservation.created_at else '',
            reservation.updated_at.isoformat() if reservation.updated_at else ''
        ]
        writer.writerow(row)
    
    return output.getvalue()
