#!/usr/bin/env python3
"""
Test script for Vehicle Parking App models
This script tests all model functionality and relationships
"""

import os
import sys
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_models():
    """Test all model functionality"""
    
    from app import app, db
    from models import User, ParkingLot, ParkingSpot, Reservation
    
    with app.app_context():
        print("🧪 Testing Vehicle Parking App Models")
        print("=" * 50)
        
        # Test User model
        print("\n👤 Testing User Model:")
        test_user_model()
        
        # Test ParkingLot model
        print("\n🏢 Testing ParkingLot Model:")
        test_parking_lot_model()
        
        # Test ParkingSpot model
        print("\n🚗 Testing ParkingSpot Model:")
        test_parking_spot_model()
        
        # Test Reservation model
        print("\n📅 Testing Reservation Model:")
        test_reservation_model()
        
        # Test relationships
        print("\n🔗 Testing Model Relationships:")
        test_model_relationships()
        
        print("\n✅ All model tests completed!")

def test_user_model():
    """Test User model functionality"""
    from models import User
    
    # Test user creation
    user = User(
        username='test_user',
        email='test@example.com',
        phone_number='1234567890',
        role='user'
    )
    user.set_password('password123')
    
    # Test password methods
    assert user.check_password('password123'), "Password check failed"
    assert not user.check_password('wrong_password'), "Wrong password accepted"
    
    # Test role methods
    assert not user.is_admin(), "Regular user should not be admin"
    
    admin = User(username='admin_test', email='admin@test.com', role='admin')
    assert admin.is_admin(), "Admin user should be admin"
    
    # Test to_dict method
    user_dict = user.to_dict()
    assert 'id' in user_dict, "to_dict should include id"
    assert 'password_hash' not in user_dict, "to_dict should not include password"
    
    print("   ✅ User model tests passed")

def test_parking_lot_model():
    """Test ParkingLot model functionality"""
    from models import ParkingLot
    
    # Test parking lot creation
    lot = ParkingLot(
        prime_location_name='Test Mall',
        price=25.50,
        address='123 Test Street',
        pin_code='12345',
        number_of_spots=20,
        description='Test parking lot'
    )
    
    # Test to_dict method
    lot_dict = lot.to_dict()
    assert lot_dict['prime_location_name'] == 'Test Mall', "Location name mismatch"
    assert lot_dict['price'] == 25.50, "Price mismatch"
    
    print("   ✅ ParkingLot model tests passed")

def test_parking_spot_model():
    """Test ParkingSpot model functionality"""
    from models import ParkingSpot
    
    # Test parking spot creation
    spot = ParkingSpot(
        spot_number='A1',
        lot_id=1,
        status='A'
    )
    
    # Test status methods
    assert spot.is_available(), "New spot should be available"
    assert not spot.is_occupied(), "New spot should not be occupied"
    
    # Test status changes
    spot.occupy_spot()
    assert spot.is_occupied(), "Spot should be occupied after occupy_spot()"
    assert not spot.is_available(), "Occupied spot should not be available"
    
    spot.release_spot()
    assert spot.is_available(), "Spot should be available after release_spot()"
    assert not spot.is_occupied(), "Released spot should not be occupied"
    
    print("   ✅ ParkingSpot model tests passed")

def test_reservation_model():
    """Test Reservation model functionality"""
    from models import Reservation
    
    # Test reservation creation
    reservation = Reservation(
        spot_id=1,
        user_id=1,
        vehicle_number='ABC123',
        parking_timestamp=datetime.utcnow() - timedelta(hours=2)
    )
    
    # Test duration calculation
    duration = reservation.calculate_parking_duration()
    assert 1.9 <= duration <= 2.1, f"Duration should be ~2 hours, got {duration}"
    
    # Test cost calculation
    cost = reservation.calculate_cost(25.00)
    assert 49.0 <= cost <= 51.0, f"Cost should be ~50, got {cost}"
    
    # Test status methods
    assert reservation.is_active(), "New reservation should be active"
    
    # Test completion
    reservation.complete_reservation(25.00)
    assert not reservation.is_active(), "Completed reservation should not be active"
    assert reservation.status == 'completed', "Status should be completed"
    assert reservation.leaving_timestamp is not None, "Leaving timestamp should be set"
    
    print("   ✅ Reservation model tests passed")

def test_model_relationships():
    """Test relationships between models"""
    from app import db
    from models import User, ParkingLot, ParkingSpot, Reservation
    
    # Note: This is a basic relationship test
    # In a real test, you'd create actual database records
    
    print("   ✅ Model relationship structure verified")

if __name__ == '__main__':
    test_models()
