#!/usr/bin/env python3
import os
import sys
from datetime import datetime

# Change to backend directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)

from app import app
from database import db
from models.user import User
from models.parking_lot import ParkingLot
from models.parking_spot import ParkingSpot
from models.reservation import Reservation

def create_admin_user():
    """Create default admin user"""
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@parkingapp.com',
            phone_number='+1234567890',
            role='admin',
            is_active=True,
            created_at=datetime.utcnow()
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        print('✅ Admin user created (username: admin, password: admin123)')
    else:
        print('✅ Admin user already exists')
    return admin_user

def create_sample_data():
    """Create sample parking lots and users for testing"""
    
    # Create sample parking lots
    sample_lots = [
        {
            'prime_location_name': 'Downtown Plaza',
            'price': 5.00,
            'address': '123 Main St, Downtown',
            'pin_code': '12345',
            'number_of_spots': 50,
            'description': 'Premium downtown parking with easy access to shopping and dining'
        },
        {
            'prime_location_name': 'Airport Terminal',
            'price': 8.00,
            'address': '456 Airport Blvd, Terminal A',
            'pin_code': '54321',
            'number_of_spots': 100,
            'description': 'Secure airport parking for travelers'
        },
        {
            'prime_location_name': 'University Campus',
            'price': 3.00,
            'address': '789 College Ave, Campus North',
            'pin_code': '67890',
            'number_of_spots': 75,
            'description': 'Affordable parking for students and faculty'
        },
        {
            'prime_location_name': 'Shopping Mall',
            'price': 4.50,
            'address': '321 Mall Dr, Shopping District',
            'pin_code': '09876',
            'number_of_spots': 200,
            'description': 'Covered parking at the largest shopping center'
        }
    ]
    
    created_lots = []
    for lot_data in sample_lots:
        existing_lot = ParkingLot.query.filter_by(
            prime_location_name=lot_data['prime_location_name']
        ).first()
        
        if not existing_lot:
            lot = ParkingLot(**lot_data)
            db.session.add(lot)
            db.session.flush()  # Get the ID
            
            # Create parking spots for this lot
            for i in range(1, lot_data['number_of_spots'] + 1):
                spot = ParkingSpot(
                    spot_number=f"P{i:03d}",
                    lot_id=lot.id,
                    status='A'  # Available
                )
                db.session.add(spot)
            
            created_lots.append(lot)
            print(f'✅ Created parking lot: {lot_data["prime_location_name"]} with {lot_data["number_of_spots"]} spots')
        else:
            print(f'✅ Parking lot already exists: {lot_data["prime_location_name"]}')
    
    # Create sample users
    sample_users = [
        {
            'username': 'john_doe',
            'email': 'john@example.com',
            'phone_number': '+1234567891',
            'password': 'user123'
        },
        {
            'username': 'jane_smith',
            'email': 'jane@example.com',
            'phone_number': '+1234567892',
            'password': 'user123'
        },
        {
            'username': 'mike_wilson',
            'email': 'mike@example.com',
            'phone_number': '+1234567893',
            'password': 'user123'
        }
    ]
    
    for user_data in sample_users:
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if not existing_user:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                phone_number=user_data['phone_number'],
                role='user',
                is_active=True,
                created_at=datetime.utcnow()
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            print(f'✅ Created user: {user_data["username"]}')
        else:
            print(f'✅ User already exists: {user_data["username"]}')
    
    return created_lots

def main():
    with app.app_context():
        print('🔧 Setting up Vehicle Parking App Database...')
        
        # Ensure instance directory exists
        os.makedirs('instance', exist_ok=True)
        
        # Drop all tables and recreate
        print('🗑️  Dropping existing tables...')
        db.drop_all()
        
        # Create all tables
        print('📊 Creating database tables...')
        db.create_all()
        
        # Create admin user
        admin_user = create_admin_user()
        
        # Create sample data
        print('📋 Creating sample data...')
        created_lots = create_sample_data()
        
        # Commit all changes
        db.session.commit()
        
        print('\n✅ Database setup completed successfully!')
        print(f'✅ Database location: {app.config["SQLALCHEMY_DATABASE_URI"]}')
        
        # Print summary
        users = User.query.all()
        lots = ParkingLot.query.all()
        spots = ParkingSpot.query.all()
        
        print(f'\n📊 Summary:')
        print(f'  - Users: {len(users)} (1 admin, {len(users)-1} regular users)')
        print(f'  - Parking Lots: {len(lots)}')
        print(f'  - Parking Spots: {len(spots)}')
        
        print(f'\n🔑 Admin Credentials:')
        print(f'  - Username: admin')
        print(f'  - Password: admin123')
        print(f'  - Email: admin@parkingapp.com')
        
        print(f'\n🔑 Sample User Credentials:')
        for user in users:
            if user.role == 'user':
                print(f'  - Username: {user.username}, Password: user123')

if __name__ == '__main__':
    main()
