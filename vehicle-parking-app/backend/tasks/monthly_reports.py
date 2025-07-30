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
    """Generate monthly report data for a user - matches dashboard logic exactly"""
    from models.reservation import Reservation
    from models.parking_lot import ParkingLot
    from models.parking_spot import ParkingSpot
    from database import db
    from sqlalchemy import func, extract
    
    # Get reservations for the month - EXACTLY like dashboard
    monthly_reservations = Reservation.query.filter(
        Reservation.user_id == user_id,
        extract('month', Reservation.created_at) == month,
        extract('year', Reservation.created_at) == year
    ).all()
    
    # Calculate statistics - EXACTLY like dashboard
    total_reservations = len(monthly_reservations)
    completed_reservations = len([r for r in monthly_reservations if r.status == 'completed'])
    
    # Use same logic as dashboard for total spent - FIXED
    total_amount_spent = 0
    total_hours_parked = 0
    
    for reservation in monthly_reservations:
        if reservation.status == 'completed' and reservation.parking_cost:
            total_amount_spent += float(reservation.parking_cost)
        
        # Calculate total hours using same logic as dashboard
        if reservation.status == 'completed':
            # Use calculate_parking_duration method if available, or fall back to total_hours
            try:
                if hasattr(reservation, 'calculate_parking_duration'):
                    duration = reservation.calculate_parking_duration()
                    if duration:
                        total_hours_parked += duration
                elif reservation.total_hours:
                    total_hours_parked += float(reservation.total_hours)
            except:
                # Fallback to manual calculation if methods fail
                if reservation.parking_timestamp and reservation.leaving_timestamp:
                    duration = reservation.leaving_timestamp - reservation.parking_timestamp
                    hours = duration.total_seconds() / 3600
                    total_hours_parked += hours
    
    # Get most used parking lot - Fixed logic
    lot_usage = {}
    lot_details = {}
    
    for reservation in monthly_reservations:
        try:
            spot = ParkingSpot.query.get(reservation.spot_id)
            if spot:
                lot = ParkingLot.query.get(spot.lot_id)
                if lot:
                    # Use prime_location_name for consistency with dashboard
                    lot_name = lot.prime_location_name or lot.location or f"Lot {lot.id}"
                    
                    if lot_name not in lot_usage:
                        lot_usage[lot_name] = 0
                        lot_details[lot_name] = {
                            'count': 0,
                            'total_cost': 0,
                            'total_hours': 0
                        }
                    
                    lot_usage[lot_name] += 1
                    lot_details[lot_name]['count'] += 1
                    
                    # Add cost only for completed reservations
                    if reservation.status == 'completed' and reservation.parking_cost:
                        lot_details[lot_name]['total_cost'] += float(reservation.parking_cost)
                    
                    # Add hours only for completed reservations
                    if reservation.status == 'completed':
                        try:
                            if hasattr(reservation, 'calculate_parking_duration'):
                                duration = reservation.calculate_parking_duration()
                                if duration:
                                    lot_details[lot_name]['total_hours'] += duration
                            elif reservation.total_hours:
                                lot_details[lot_name]['total_hours'] += float(reservation.total_hours)
                        except:
                            pass
        except Exception as e:
            print(f"Error processing reservation {reservation.id}: {e}")
            continue
    
    # Find most used lot
    most_used_lot = ('None', 0)
    if lot_usage:
        most_used_lot = max(lot_usage.items(), key=lambda x: x[1])
    
    # Get daily usage pattern
    daily_usage = {}
    weekday_usage = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}  # Monday=0, Sunday=6
    
    for reservation in monthly_reservations:
        day = reservation.created_at.day
        weekday = reservation.created_at.weekday()
        
        if day not in daily_usage:
            daily_usage[day] = 0
        daily_usage[day] += 1
        weekday_usage[weekday] += 1
    
    # Calculate savings vs daily rate (improved calculation)
    estimated_savings = 0
    if completed_reservations > 0:
        for reservation in [r for r in monthly_reservations if r.status == 'completed']:
            try:
                if reservation.parking_cost:
                    # Get actual duration
                    actual_duration = 0
                    if hasattr(reservation, 'calculate_parking_duration'):
                        actual_duration = reservation.calculate_parking_duration() or 0
                    elif reservation.total_hours:
                        actual_duration = float(reservation.total_hours)
                    
                    if actual_duration > 0 and actual_duration < 8:  # If parked less than 8 hours
                        spot = ParkingSpot.query.get(reservation.spot_id)
                        if spot:
                            lot = ParkingLot.query.get(spot.lot_id)
                            if lot and hasattr(lot, 'price'):
                                # Assume daily rate is 8x hourly rate
                                daily_rate = float(lot.price) * 8
                                actual_cost = float(reservation.parking_cost)
                                savings = max(0, daily_rate - actual_cost)
                                estimated_savings += savings
            except Exception as e:
                print(f"Error calculating savings for reservation {reservation.id}: {e}")
                continue
    
    return {
        'total_reservations': total_reservations,
        'completed_reservations': completed_reservations,
        'total_amount_spent': round(total_amount_spent, 2),
        'total_hours_parked': round(total_hours_parked, 2),
        'average_cost_per_reservation': round(total_amount_spent / completed_reservations, 2) if completed_reservations > 0 else 0,
        'average_hours_per_reservation': round(total_hours_parked / completed_reservations, 2) if completed_reservations > 0 else 0,
        'most_used_lot': most_used_lot,
        'lot_details': lot_details,
        'daily_usage': daily_usage,
        'weekday_usage': weekday_usage,
        'estimated_savings': round(max(0, estimated_savings), 2),
        'reservations': [r.to_dict() for r in monthly_reservations]
    }

def generate_monthly_report_html(user, report_data, month, year):
    """Generate HTML for monthly report"""
    month_names = [
        '', 'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    # Generate weekday usage chart data
    weekday_chart_data = []
    for i in range(7):
        weekday_chart_data.append({
            'day': weekday_names[i],
            'count': report_data['weekday_usage'][i]
        })
    
    # Generate lot details table
    lot_details_html = ""
    if report_data['lot_details']:
        lot_details_html = """
        <div class="lot-details-section">
            <h3>&#127970; Parking Lot Usage Breakdown</h3>
            <table class="lot-details-table">
                <thead>
                    <tr>
                        <th>Parking Lot</th>
                        <th>Visits</th>
                        <th>Total Hours</th>
                        <th>Total Spent</th>
                        <th>Avg Cost/Visit</th>
                    </tr>
                </thead>
                <tbody>
        """
        for lot_name, details in report_data['lot_details'].items():
            avg_cost = details['total_cost'] / details['count'] if details['count'] > 0 else 0
            lot_details_html += f"""
                    <tr>
                        <td>{lot_name}</td>
                        <td>{details['count']}</td>
                        <td>{details['total_hours']:.1f}</td>
                        <td>Rs.{details['total_cost']:.2f}</td>
                        <td>Rs.{avg_cost:.2f}</td>
                    </tr>
            """
        lot_details_html += """
                </tbody>
            </table>
        </div>
        """
    
    # Generate daily usage chart
    daily_chart_html = ""
    # Daily usage pattern removed as requested
    
    # Generate weekday usage chart
    weekday_chart_html = ""
    # Weekday usage pattern removed as requested
    
    # Generate daily usage chart
    daily_chart_html = ""
    # Daily usage pattern removed as requested
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Monthly Parking Report - {month_names[month]} {year}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
                color: white;
                padding: 30px;
                text-align: center;
                position: relative;
            }}
            .header::before {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="80" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="40" cy="60" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
                position: relative;
                z-index: 1;
            }}
            .header p {{
                margin: 10px 0 0;
                font-size: 1.2em;
                opacity: 0.9;
                position: relative;
                z-index: 1;
            }}
            .content {{
                padding: 30px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 25px;
                border-radius: 10px;
                text-align: center;
                border-left: 5px solid #4CAF50;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}
            .stat-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }}
            .stat-value {{
                font-size: 2.5em;
                font-weight: bold;
                color: #2c3e50;
                margin: 0;
            }}
            .stat-label {{
                color: #666;
                margin-top: 5px;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .savings-card {{
                background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
                color: white;
                border-left-color: #1e8449;
            }}
            .savings-card .stat-value {{
                color: white;
            }}
            .savings-card .stat-label {{
                color: rgba(255,255,255,0.9);
            }}
            .section {{
                margin: 30px 0;
                padding: 25px;
                background: #f8f9fa;
                border-radius: 10px;
                border-left: 4px solid #4CAF50;
            }}
            .section h3 {{
                margin-top: 0;
                color: #2c3e50;
                font-size: 1.3em;
                display: flex;
                align-items: center;
                gap: 8px;
            }}
            .lot-details-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .lot-details-table th {{
                background: #4CAF50;
                color: white;
                padding: 15px;
                text-align: left;
                font-weight: 600;
            }}
            .lot-details-table td {{
                padding: 12px 15px;
                border-bottom: 1px solid #eee;
            }}
            .lot-details-table tr:hover {{
                background: #f8f9fa;
            }}
            .reservations-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .reservations-table th {{
                background: #4CAF50;
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
                font-size: 0.9em;
            }}
            .reservations-table td {{
                padding: 10px 12px;
                border-bottom: 1px solid #eee;
                font-size: 0.85em;
            }}
            .reservations-table tr:hover {{
                background: #f8f9fa;
            }}
            .status-completed {{
                background: #d4edda;
                color: #1e7e34;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 0.8em;
            }}
            .status-cancelled {{
                background: #f8d7da;
                color: #721c24;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 0.8em;
            }}
            .status-active {{
                background: #fff3cd;
                color: #856404;
                padding: 3px 8px;
                border-radius: 12px;
                font-size: 0.8em;
            }}
            .footer {{
                background: #2c3e50;
                color: white;
                padding: 20px;
                text-align: center;
                font-size: 0.9em;
            }}
            .footer a {{
                color: #4CAF50;
                text-decoration: none;
            }}
            .no-data {{
                text-align: center;
                color: #666;
                font-style: italic;
                padding: 40px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>&#128663; Monthly Parking Report</h1>
                <p>Hello {user.username}! Here's your parking activity for {month_names[month]} {year}</p>
            </div>
            
            <div class="content">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{report_data['total_reservations']}</div>
                        <div class="stat-label">Total Bookings</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{report_data['completed_reservations']}</div>
                        <div class="stat-label">Completed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">Rs.{report_data['total_amount_spent']:.2f}</div>
                        <div class="stat-label">Total Spent</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{report_data['total_hours_parked']:.1f}h</div>
                        <div class="stat-label">Hours Parked</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">Rs.{report_data['average_cost_per_reservation']:.2f}</div>
                        <div class="stat-label">Avg Cost/Booking</div>
                    </div>
                    <div class="stat-card savings-card">
                        <div class="stat-value">Rs.{report_data['estimated_savings']:.2f}</div>
                        <div class="stat-label">Estimated Savings</div>
                    </div>
                </div>
                
                <div class="section">
                    <h3>&#127942; Most Used Parking Lot</h3>
                    <p><strong>{report_data['most_used_lot'][0]}</strong> - {report_data['most_used_lot'][1]} visits</p>
                </div>
                
                {lot_details_html}
                
                {weekday_chart_html}
                
                {daily_chart_html}
                
                <div class="section">
                    <h3>&#128203; All Reservations</h3>
                    {"<div class='no-data'>No reservations found for this month.</div>" if not report_data['reservations'] else ""}"""
    
    if report_data['reservations']:
        html_template += """
                    <table class="reservations-table">
                        <thead>
                            <tr>
                                <th>Date</th>
                                <th>Parking Lot</th>
                                <th>Spot</th>
                                <th>Hours</th>
                                <th>Cost</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>"""
        
        from models.parking_spot import ParkingSpot
        from models.parking_lot import ParkingLot
        from datetime import datetime
        
        # Sort reservations by created_at (now they are dictionaries)
        sorted_reservations = sorted(report_data['reservations'], 
                                   key=lambda x: datetime.fromisoformat(x['created_at']) if x.get('created_at') else datetime.min, 
                                   reverse=True)
        
        for reservation_dict in sorted_reservations:
            spot = ParkingSpot.query.get(reservation_dict.get('spot_id'))
            lot_name = "N/A"
            if spot:
                lot = ParkingLot.query.get(spot.lot_id)
                if lot:
                    lot_name = lot.prime_location_name or lot.location
            
            status = reservation_dict.get('status', 'unknown')
            status_class = f"status-{status}"
            hours = reservation_dict.get('total_hours', 0) or 0
            cost = reservation_dict.get('parking_cost', 0) or 0
            
            # Parse the created_at date
            created_at_str = reservation_dict.get('created_at', '')
            try:
                if created_at_str:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    date_str = created_at.strftime('%d %b, %Y')
                else:
                    date_str = 'N/A'
            except:
                date_str = 'N/A'
            
            html_template += f"""
                            <tr>
                                <td>{date_str}</td>
                                <td>{lot_name}</td>
                                <td>{spot.spot_number if spot else 'N/A'}</td>
                                <td>{hours:.1f}h</td>
                                <td>Rs.{cost:.2f}</td>
                                <td><span class="{status_class}">{status.title()}</span></td>
                            </tr>"""
        
        html_template += """
                        </tbody>
                    </table>"""
    
    html_template += """
                </div>
            </div>
            
            <div class="footer">
                <p>Thank you for using our parking service! 🚗</p>
                <p>For support, contact us at <a href="mailto:support@parkingapp.com">support@parkingapp.com</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_template
    
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

# Task wrapper function for external access
@celery_app.task(bind=True)
def send_monthly_reports_task(self, month=None, year=None):
    """Task wrapper for sending monthly reports with specific month/year"""
    try:
        from models.user import User
        from database import db
        
        # Use provided month/year or current
        now = datetime.utcnow()
        report_month = month or now.month
        report_year = year or now.year
        
        users = User.query.filter_by(role='user').all()
        successful_sends = 0
        failed_sends = 0
        
        for user in users:
            try:
                # Generate report data
                report_data = generate_monthly_report_data(user.id, report_month, report_year)
                
                # Only send if user has activity
                if report_data['total_reservations'] > 0:
                    # Generate HTML report
                    html_report = generate_monthly_report_html(user, report_data, report_month, report_year)
                    
                    # Send email
                    subject = f"Monthly Parking Report - {report_month}/{report_year}"
                    send_email(user.email, subject, html_report)
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

# Email function for sending HTML emails
def send_email(to_email, subject, html_content):
    """Send HTML email"""
    if not Config.MAIL_SERVER:
        print("⚠️ Email server not configured")
        return
    
    msg = MIMEMultipart('alternative')
    msg['From'] = Config.MAIL_USERNAME
    msg['To'] = to_email
    msg['Subject'] = subject
    
    # Attach HTML content
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    # Send email
    with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
        if Config.MAIL_USE_TLS:
            server.starttls()
        if Config.MAIL_USERNAME and Config.MAIL_PASSWORD:
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.send_message(msg)
