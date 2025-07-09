from flask import current_app
import csv
import os
from celery import shared_task
from datetime import datetime
from models.reservation import Reservation

@shared_task
def export_user_parking_details(user_id):
    reservations = Reservation.query.filter_by(user_id=user_id).all()
    if not reservations:
        return "No reservations found for this user."

    file_path = f"exports/user_{user_id}_parking_details_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Slot ID', 'Spot ID', 'Parking Timestamp', 'Leaving Timestamp', 'Cost'])
        
        for reservation in reservations:
            writer.writerow([
                reservation.spot_id,
                reservation.id,
                reservation.parking_timestamp,
                reservation.leaving_timestamp,
                reservation.parking_cost
            ])
    
    return f"Exported user parking details to {file_path}"