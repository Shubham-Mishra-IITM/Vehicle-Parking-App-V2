#!/usr/bin/env python3
"""
Simple database initialization script for Vehicle Parking App
This script creates all tables and sets up the initial admin user
"""

import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Create a simple app for initialization
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# Simple model definitions for initialization
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    role = db.Column(db.String(20), default='user', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)

class ParkingLot(db.Model):
    __tablename__ = 'parking_lots'

    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(10), nullable=False)
    number_of_spots = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class ParkingSpot(db.Model):
    __tablename__ = 'parking_spots'

    id = db.Column(db.Integer, primary_key=True)
    spot_number = db.Column(db.String(10), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lots.id'), nullable=False)
    status = db.Column(db.String(1), default='A', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class Reservation(db.Model):
    __tablename__ = 'reservations'

    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spots.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Numeric(10, 2), nullable=True)
    total_hours = db.Column(db.Numeric(5, 2), nullable=True)
    status = db.Column(db.String(20), default='active', nullable=False)
    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

def init_database():
    """Initialize the database with tables and admin user"""
    
    with app.app_context():
        print("🔧 Creating database tables...")
        
        # Drop all tables (for development - remove in production)
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("✅ Database tables created successfully!")
        
        # Create admin user
        create_admin_user()
        
        # Create sample data for testing
        create_sample_data()
        
        print("🎉 Database initialization completed!")

def create_admin_user():
    """Create the default admin user"""
    from werkzeug.security import generate_password_hash
    
    print("👑 Creating admin user...")
    
    # Create admin user with a simple password hash method
    admin_user = User(
        username='admin',
        email='admin@parkingapp.com',
        password_hash=generate_password_hash('admin123', method='pbkdf2:sha256'),
        role='admin',
        phone_number='1234567890',
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    db.session.add(admin_user)
    db.session.commit()
    
    print("✅ Admin user created successfully!")
    print("   Username: admin")
    print("   Password: admin123")
    print("   Email: admin@parkingapp.com")

def create_sample_data():
    """Create sample parking lots and spots for testing"""
    
    print("🏗️  Creating sample data...")
    
    # Sample parking lots
    sample_lots = [
        {
            'prime_location_name': 'City Center Mall',
            'price': 25.00,
            'address': '123 Main Street, Downtown, City',
            'pin_code': '12345',
            'number_of_spots': 50,
            'description': 'Premium parking facility at the heart of the city',
            'latitude': 40.7128,
            'longitude': -74.0060
        },
        {
            'prime_location_name': 'Airport Terminal',
            'price': 40.00,
            'address': '456 Airport Road, Terminal Building',
            'pin_code': '54321',
            'number_of_spots': 100,
            'description': 'Convenient parking for airport travelers',
            'latitude': 40.6413,
            'longitude': -73.7781
        },
        {
            'prime_location_name': 'Business District',
            'price': 30.00,
            'address': '789 Corporate Ave, Business Quarter',
            'pin_code': '67890',
            'number_of_spots': 75,
            'description': 'Professional parking for office workers',
            'latitude': 40.7589,
            'longitude': -73.9851
        }
    ]
    
    for lot_data in sample_lots:
        # Create parking lot
        parking_lot = ParkingLot(**lot_data)
        db.session.add(parking_lot)
        db.session.flush()  # Get the ID
        
        # Create parking spots for this lot
        create_parking_spots(parking_lot)
    
    # Create a sample user
    from werkzeug.security import generate_password_hash
    sample_user = User(
        username='john_doe',
        email='john@example.com',
        password_hash=generate_password_hash('password123', method='pbkdf2:sha256'),
        role='user',
        phone_number='9876543210',
        is_active=True,
        created_at=datetime.utcnow()
    )
    db.session.add(sample_user)
    
    db.session.commit()
    print("✅ Sample data created successfully!")

def create_parking_spots(parking_lot):
    """Create parking spots for a given parking lot"""
    
    spots_per_section = 10
    sections = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    
    spot_count = 0
    for section in sections:
        if spot_count >= parking_lot.number_of_spots:
            break
            
        for spot_num in range(1, spots_per_section + 1):
            if spot_count >= parking_lot.number_of_spots:
                break
                
            spot_number = f"{section}{spot_num}"
            parking_spot = ParkingSpot(
                spot_number=spot_number,
                lot_id=parking_lot.id,
                status='A',  # Available
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(parking_spot)
            spot_count += 1

def reset_database():
    """Reset the database (useful for development)"""
    
    print("⚠️  Resetting database...")
    with app.app_context():
        db.drop_all()
        print("🗑️  All tables dropped!")
        init_database()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize the parking app database')
    parser.add_argument('--reset', action='store_true', 
                       help='Reset the database (drops all tables)')
    
    args = parser.parse_args()
    
    if args.reset:
        reset_database()
    else:
        init_database()
