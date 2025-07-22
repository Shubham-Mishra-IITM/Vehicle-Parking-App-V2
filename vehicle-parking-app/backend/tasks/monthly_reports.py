from celery import current_app as celery_app
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from config import Config

@celery_app.task(bind=True)
def send_monthly_reports(self):
    """Send monthly activity reports to all users"""
    try:
        from models.user import User
        from models.reservation import Reservation
        from models.parking_lot import ParkingLot
        from models.parking_spot import ParkingSpot
        from database import db
        from sqlalchemy import func, extract
        
        # Get current month and previous month
        now = datetime.utcnow()
        current_month = now.month
        current_year = now.year
        
        # For testing, we'll use last month
        if current_month == 1:
            report_month = 12
            report_year = current_year - 1
        else:
            report_month = current_month - 1
            report_year = current_year
        
        # Get all active users
        users = User.query.filter_by(role='user', is_active=True).all()
        
        successful_sends = 0
        failed_sends = 0
        
        for user in users:
            try:
                # Generate monthly report for user
                report_data = generate_monthly_report_data(user.id, report_month, report_year)
                
                if report_data['total_reservations'] > 0:  # Only send if user had activity
                    # Generate HTML report
                    html_report = generate_monthly_report_html(user, report_data, report_month, report_year)
                    
                    # Send email
                    if user.email and Config.MAIL_SERVER:
                        send_monthly_report_email(user, html_report, report_month, report_year)
                
                successful_sends += 1
                
            except Exception as e:
                print(f"Failed to send monthly report to {user.username}: {str(e)}")
                failed_sends += 1
        
        return {
            'status': 'completed',
            'users_processed': len(users),
            'successful_sends': successful_sends,
            'failed_sends': failed_sends,
            'report_month': report_month,
            'report_year': report_year,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

def generate_monthly_report_data(user_id, month, year):
    """Generate monthly report data for a user"""
    from models.reservation import Reservation
    from models.parking_lot import ParkingLot
    from models.parking_spot import ParkingSpot
    from database import db
    from sqlalchemy import func, extract
    
    # Get reservations for the month
    monthly_reservations = Reservation.query.filter(
        Reservation.user_id == user_id,
        extract('month', Reservation.created_at) == month,
        extract('year', Reservation.created_at) == year
    ).all()
    
    # Calculate statistics
    total_reservations = len(monthly_reservations)
    completed_reservations = len([r for r in monthly_reservations if r.status == 'completed'])
    
    total_amount_spent = sum([
        float(r.parking_cost) for r in monthly_reservations 
        if r.parking_cost and r.status == 'completed'
    ])
    
    total_hours_parked = sum([
        float(r.total_hours) for r in monthly_reservations 
        if r.total_hours and r.status == 'completed'
    ])
    
    # Get most used parking lot
    if monthly_reservations:
        lot_usage = {}
        for reservation in monthly_reservations:
            spot = ParkingSpot.query.get(reservation.spot_id)
            if spot:
                lot = ParkingLot.query.get(spot.lot_id)
                if lot:
                    if lot.prime_location_name not in lot_usage:
                        lot_usage[lot.prime_location_name] = 0
                    lot_usage[lot.prime_location_name] += 1
        
        most_used_lot = max(lot_usage.items(), key=lambda x: x[1]) if lot_usage else ('None', 0)
    else:
        most_used_lot = ('None', 0)
    
    # Get daily usage pattern
    daily_usage = {}
    for reservation in monthly_reservations:
        day = reservation.created_at.day
        if day not in daily_usage:
            daily_usage[day] = 0
        daily_usage[day] += 1
    
    return {
        'total_reservations': total_reservations,
        'completed_reservations': completed_reservations,
        'total_amount_spent': total_amount_spent,
        'total_hours_parked': total_hours_parked,
        'average_cost_per_reservation': total_amount_spent / completed_reservations if completed_reservations > 0 else 0,
        'average_hours_per_reservation': total_hours_parked / completed_reservations if completed_reservations > 0 else 0,
        'most_used_lot': most_used_lot,
        'daily_usage': daily_usage,
        'reservations': monthly_reservations
    }

def generate_monthly_report_html(user, report_data, month, year):
    """Generate HTML monthly report"""
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    month_name = month_names[month - 1]
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
            .content {{ margin: 20px 0; }}
            .stats-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .stats-table th, .stats-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            .stats-table th {{ background-color: #f2f2f2; }}
            .chart-container {{ margin: 20px 0; }}
            .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Monthly Parking Report</h1>
            <h2>{month_name} {year}</h2>
            <p>Report for: {user.username}</p>
        </div>
        
        <div class="content">
            <h3>Parking Summary</h3>
            <table class="stats-table">
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Total Reservations</td>
                    <td>{report_data['total_reservations']}</td>
                </tr>
                <tr>
                    <td>Completed Reservations</td>
                    <td>{report_data['completed_reservations']}</td>
                </tr>
                <tr>
                    <td>Total Amount Spent</td>
                    <td>${report_data['total_amount_spent']:.2f}</td>
                </tr>
                <tr>
                    <td>Total Hours Parked</td>
                    <td>{report_data['total_hours_parked']:.2f} hours</td>
                </tr>
                <tr>
                    <td>Average Cost per Reservation</td>
                    <td>${report_data['average_cost_per_reservation']:.2f}</td>
                </tr>
                <tr>
                    <td>Average Hours per Reservation</td>
                    <td>{report_data['average_hours_per_reservation']:.2f} hours</td>
                </tr>
                <tr>
                    <td>Most Used Parking Lot</td>
                    <td>{report_data['most_used_lot'][0]} ({report_data['most_used_lot'][1]} times)</td>
                </tr>
            </table>
            
            <h3>Reservation Details</h3>
            <table class="stats-table">
                <tr>
                    <th>Date</th>
                    <th>Parking Lot</th>
                    <th>Duration</th>
                    <th>Cost</th>
                    <th>Status</th>
                </tr>
    """
    
    # Add reservation details
    for reservation in report_data['reservations']:
        from models.parking_spot import ParkingSpot
        from models.parking_lot import ParkingLot
        
        spot = ParkingSpot.query.get(reservation.spot_id)
        lot = ParkingLot.query.get(spot.lot_id) if spot else None
        
        html += f"""
                <tr>
                    <td>{reservation.parking_timestamp.strftime('%Y-%m-%d %H:%M') if reservation.parking_timestamp else 'N/A'}</td>
                    <td>{lot.prime_location_name if lot else 'Unknown'}</td>
                    <td>{float(reservation.total_hours):.2f} hours</td>
                    <td>${float(reservation.parking_cost):.2f}</td>
                    <td>{reservation.status.title()}</td>
                </tr>
        """
    
    html += """
            </table>
        </div>
        
        <div class="footer">
            <p>Thank you for using our parking service!</p>
            <p>For any questions, please contact our support team.</p>
        </div>
    </body>
    </html>
    """
    
    return html

def send_monthly_report_email(user, html_report, month, year):
    """Send monthly report via email"""
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    month_name = month_names[month - 1]
    subject = f"Your Monthly Parking Report - {month_name} {year}"
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = Config.MAIL_DEFAULT_SENDER
    msg['To'] = user.email
    
    # Create HTML part
    html_part = MIMEText(html_report, 'html')
    msg.attach(html_part)
    
    # Send email
    with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
        if Config.MAIL_USE_TLS:
            server.starttls()
        if Config.MAIL_USERNAME and Config.MAIL_PASSWORD:
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.send_message(msg)
