from celery import shared_task
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from backend import app, db
from backend.models import Reservation, User

mail = Mail(app)

@shared_task
def send_monthly_report(user_id):
    user = User.query.get(user_id)
    if user:
        reservations = Reservation.query.filter_by(user_id=user.id).all()
        total_spots_booked = len(reservations)
        total_cost = sum(reservation.parking_cost for reservation in reservations)
        most_used_parking_lot = get_most_used_parking_lot(reservations)

        report = f"""
        Monthly Activity Report for {user.username}
        
        Total Parking Spots Booked: {total_spots_booked}
        Total Amount Spent: ${total_cost:.2f}
        Most Used Parking Lot: {most_used_parking_lot}
        
        Thank you for using our parking service!
        """

        msg = Message("Monthly Activity Report", sender="noreply@vehicleparkingapp.com", recipients=[user.email])
        msg.body = report
        mail.send(msg)

def get_most_used_parking_lot(reservations):
    lot_usage = {}
    for reservation in reservations:
        lot_id = reservation.spot.lot_id
        if lot_id in lot_usage:
            lot_usage[lot_id] += 1
        else:
            lot_usage[lot_id] = 1
    most_used_lot_id = max(lot_usage, key=lot_usage.get)
    return most_used_lot_id  # You may want to return the actual lot name instead of ID.