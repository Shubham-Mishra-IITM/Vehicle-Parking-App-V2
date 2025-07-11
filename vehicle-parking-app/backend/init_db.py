#!/usr/bin/env python3
"""
Database initialization script for Vehicle Parking App
This script creates all tables and sets up the initial admin user
"""

import os
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, ParkingLot, ParkingSpot, Reservation

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
    
    print("👑 Creating admin user...")
    
    # Check if admin already exists
    admin = db.session.query(User).filter_by(role='admin').first()
    if admin:
        print("⚠️  Admin user already exists!")
        return
    
    # Create admin user
    admin_user = User(
        username='admin',
        email='admin@parkingapp.com',
        role='admin',
        phone_number='1234567890',
        is_active=True,
        created_at=datetime.utcnow()
    )
    admin_user.set_password('admin123')  # Change this in production!
    
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
    sample_user = User(
        username='john_doe',
        email='john@example.com',
        role='user',
        phone_number='9876543210',
        is_active=True,
        created_at=datetime.utcnow()
    )
    sample_user.set_password('password123')
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
