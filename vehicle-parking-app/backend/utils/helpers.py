from datetime import datetime, timedelta
import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone_number(phone):
    """Validate phone number format"""
    if not phone:
        return True  # Phone is optional
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's 10-15 digits
    return 10 <= len(digits_only) <= 15

def validate_vehicle_number(vehicle_number):
    """Validate vehicle number format"""
    if not vehicle_number:
        return False
    
    # Remove spaces and convert to uppercase
    cleaned = vehicle_number.replace(' ', '').upper()
    
    # Basic validation - should be 6-10 characters, alphanumeric
    return 6 <= len(cleaned) <= 10 and cleaned.isalnum()

def validate_pin_code(pin_code):
    """Validate pin code format"""
    if not pin_code:
        return False
    
    # Remove spaces
    cleaned = pin_code.replace(' ', '')
    
    # Should be 5-10 digits
    return cleaned.isdigit() and 5 <= len(cleaned) <= 10

def validate_price(price):
    """Validate price value"""
    try:
        price_float = float(price)
        return price_float >= 0
    except (ValueError, TypeError):
        return False

def validate_number_of_spots(spots):
    """Validate number of parking spots"""
    try:
        spots_int = int(spots)
        return 1 <= spots_int <= 1000  # Reasonable limit
    except (ValueError, TypeError):
        return False

def validate_coordinates(latitude, longitude):
    """Validate latitude and longitude"""
    if latitude is None and longitude is None:
        return True  # Optional fields
    
    if latitude is None or longitude is None:
        return False  # Both should be provided if one is provided
    
    try:
        lat = float(latitude)
        lng = float(longitude)
        return -90 <= lat <= 90 and -180 <= lng <= 180
    except (ValueError, TypeError):
        return False

def format_currency(amount):
    """Format amount as currency"""
    try:
        return f"${float(amount):.2f}"
    except (ValueError, TypeError):
        return "$0.00"

def format_duration(hours):
    """Format duration in hours to human readable format"""
    try:
        hours_float = float(hours)
        
        if hours_float < 1:
            minutes = int(hours_float * 60)
            return f"{minutes} minutes"
        elif hours_float < 24:
            return f"{hours_float:.1f} hours"
        else:
            days = int(hours_float // 24)
            remaining_hours = hours_float % 24
            if remaining_hours > 0:
                return f"{days} days, {remaining_hours:.1f} hours"
            else:
                return f"{days} days"
    except (ValueError, TypeError):
        return "0 minutes"

def calculate_parking_cost(start_time, end_time, hourly_rate):
    """Calculate parking cost based on duration and hourly rate"""
    try:
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        
        duration = end_time - start_time
        hours = duration.total_seconds() / 3600
        
        # Minimum charge for 1 hour
        billable_hours = max(1, hours)
        
        cost = billable_hours * float(hourly_rate)
        return round(cost, 2)
    
    except Exception:
        return 0.0

def get_parking_statistics(reservations):
    """Calculate parking statistics from reservations"""
    if not reservations:
        return {
            'total_reservations': 0,
            'completed_reservations': 0,
            'active_reservations': 0,
            'cancelled_reservations': 0,
            'total_revenue': 0.0,
            'average_duration': 0.0,
            'average_cost': 0.0
        }
    
    stats = {
        'total_reservations': len(reservations),
        'completed_reservations': 0,
        'active_reservations': 0,
        'cancelled_reservations': 0,
        'total_revenue': 0.0,
        'total_duration': 0.0
    }
    
    for reservation in reservations:
        if reservation.status == 'completed':
            stats['completed_reservations'] += 1
            if reservation.parking_cost:
                stats['total_revenue'] += float(reservation.parking_cost)
            if reservation.total_hours:
                stats['total_duration'] += float(reservation.total_hours)
        elif reservation.status == 'active':
            stats['active_reservations'] += 1
        elif reservation.status == 'cancelled':
            stats['cancelled_reservations'] += 1
    
    # Calculate averages
    if stats['completed_reservations'] > 0:
        stats['average_duration'] = stats['total_duration'] / stats['completed_reservations']
        stats['average_cost'] = stats['total_revenue'] / stats['completed_reservations']
    else:
        stats['average_duration'] = 0.0
        stats['average_cost'] = 0.0
    
    # Remove total_duration as it's not needed in the final result
    del stats['total_duration']
    
    return stats

def paginate_results(query, page, per_page, max_per_page=100):
    """Paginate query results"""
    page = max(1, page)
    per_page = min(max(1, per_page), max_per_page)
    
    return query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

def generate_spot_number(lot_id, spot_index):
    """Generate parking spot number"""
    return f"L{lot_id:03d}S{spot_index:03d}"

def is_business_hours(datetime_obj=None):
    """Check if given time is within business hours"""
    if datetime_obj is None:
        datetime_obj = datetime.utcnow()
    
    # Business hours: 6 AM to 10 PM
    hour = datetime_obj.hour
    return 6 <= hour <= 22

def get_peak_hours_multiplier(datetime_obj=None):
    """Get pricing multiplier for peak hours"""
    if datetime_obj is None:
        datetime_obj = datetime.utcnow()
    
    hour = datetime_obj.hour
    day_of_week = datetime_obj.weekday()  # 0 = Monday, 6 = Sunday
    
    # Peak hours: 7-9 AM and 5-7 PM on weekdays
    if day_of_week < 5:  # Weekdays
        if (7 <= hour <= 9) or (17 <= hour <= 19):
            return 1.5  # 50% markup
    
    # Weekend premium
    if day_of_week >= 5:  # Weekend
        return 1.2  # 20% markup
    
    return 1.0  # Regular pricing

def sanitize_string(input_string, max_length=None):
    """Sanitize string input"""
    if not input_string:
        return ""
    
    # Remove leading/trailing whitespace
    cleaned = str(input_string).strip()
    
    # Limit length if specified
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned

def generate_report_filename(report_type, user_id=None, timestamp=None):
    """Generate standardized report filename"""
    if timestamp is None:
        timestamp = datetime.utcnow()
    
    timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
    
    if user_id:
        return f"{report_type}_user_{user_id}_{timestamp_str}.csv"
    else:
        return f"{report_type}_{timestamp_str}.csv"
