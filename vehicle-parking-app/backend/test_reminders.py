#!/usr/bin/env python3
"""
Test script for the daily reminders system
"""

import os
import sys
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        from tasks.daily_reminders import send_daily_reminders, send_sms_reminder, send_email_reminder, send_google_chat_reminder
        print("✅ Daily reminders module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import daily reminders: {e}")
        return False
    
    try:
        from tasks.celery_app import celery
        print("✅ Celery app imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Celery app: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests module available")
    except ImportError:
        print("⚠️  Requests module not available (Google Chat won't work)")
    
    try:
        from twilio.rest import Client
        print("✅ Twilio module available")
    except ImportError:
        print("⚠️  Twilio module not available (SMS won't work)")
    
    return True

def test_config():
    """Test configuration variables"""
    print("\nTesting configuration...")
    
    from config import Config
    
    # Check Redis configuration
    print(f"Redis URL: {Config.REDIS_URL}")
    print(f"Celery Broker: {Config.CELERY_BROKER_URL}")
    
    # Check notification configurations
    configs = [
        ("Email Server", Config.MAIL_SERVER),
        ("Email Username", Config.MAIL_USERNAME),
        ("Google Chat Webhook", Config.GOOGLE_CHAT_WEBHOOK_URL),
        ("Twilio Account SID", Config.TWILIO_ACCOUNT_SID),
        ("Twilio Phone Number", Config.TWILIO_PHONE_NUMBER)
    ]
    
    for name, value in configs:
        if value:
            print(f"✅ {name}: Configured")
        else:
            print(f"⚠️  {name}: Not configured")

def test_database():
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        from app import app
        from database import db
        from models.user import User
        from models.parking_lot import ParkingLot
        
        # Test database connection within Flask app context
        with app.app_context():
            user_count = User.query.count()
            lot_count = ParkingLot.query.count()
            
            print(f"✅ Database connected successfully")
            print(f"   Users: {user_count}")
            print(f"   Parking lots: {lot_count}")
        
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_celery():
    """Test Celery connection"""
    print("\nTesting Celery connection...")
    
    try:
        from tasks.celery_app import celery
        
        # Try to ping Celery
        result = celery.control.ping(timeout=1)
        if result:
            print("✅ Celery workers are running")
            for worker, response in result[0].items():
                print(f"   Worker: {worker}")
        else:
            print("⚠️  No Celery workers found (this is normal if not started yet)")
        
        return True
    except Exception as e:
        print(f"❌ Celery connection failed: {e}")
        return False

def test_task_registration():
    """Test if tasks are properly registered"""
    print("\nTesting task registration...")
    
    try:
        from tasks.celery_app import celery
        
        registered_tasks = celery.tasks.keys()
        expected_tasks = [
            'tasks.daily_reminders.send_daily_reminders',
            'tasks.daily_reminders.send_admin_daily_summary',
            'tasks.daily_reminders.send_new_parking_lot_notifications'
        ]
        
        for task in expected_tasks:
            if task in registered_tasks:
                print(f"✅ {task}")
            else:
                print(f"❌ {task} not registered")
        
        return True
    except Exception as e:
        print(f"❌ Task registration test failed: {e}")
        return False

def test_reminders_directly():
    """Test daily reminders functionality directly (without Celery)"""
    print("\nTesting daily reminders functionality directly...")
    
    try:
        from app import app
        from tasks.daily_reminders import send_email_reminder
        from models.user import User
        from models.reservation import Reservation
        from database import db
        from datetime import datetime, timedelta
        
        with app.app_context():
            # Get users who haven't made a reservation in the last 3 days (same logic as the task)
            three_days_ago = datetime.utcnow() - timedelta(days=3)
            
            inactive_users = db.session.query(User).filter(
                User.role == 'user',
                User.is_active == True,
                db.or_(
                    # Users with no reservations at all
                    ~User.id.in_(
                        db.session.query(Reservation.user_id).distinct()
                    ),
                    # Users with no recent reservations (last 3 days)
                    ~User.id.in_(
                        db.session.query(Reservation.user_id).filter(
                            Reservation.created_at >= three_days_ago
                        )
                    )
                )
            ).all()
            
            print(f"✅ Found {len(inactive_users)} inactive users (3+ days)")
            
            # Test with first inactive user if any exist
            if inactive_users:
                user = inactive_users[0]
                print(f"   Testing with user: {user.username} ({user.email})")
                
                # Test email reminder (will show what would be sent)
                try:
                    result = send_email_reminder(user, dry_run=True)
                    if result:
                        print("✅ Email reminder function works (dry run)")
                    else:
                        print("⚠️  Email reminder function returned False (no email config)")
                except Exception as e:
                    print(f"⚠️  Email reminder test failed: {e}")
                    
            else:
                print("   No inactive users found for testing")
            
            # Test admin users query
            admin_users = User.query.filter_by(role='admin').all()
            print(f"✅ Found {len(admin_users)} admin users for summaries")
            
        return True
        
    except Exception as e:
        print(f"❌ Direct reminders test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚗 Vehicle Parking App - Daily Reminders Test")
    print("=" * 50)
    print(f"Test started at: {datetime.now()}")
    print()
    
    tests = [
        test_imports,
        test_config,
        test_database,
        test_celery,
        test_task_registration,
        test_reminders_directly
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
        print()
    
    # Summary
    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! The daily reminders system is ready.")
    else:
        print("⚠️  Some tests failed. Check the configuration and setup.")
    
    print("\nNext steps:")
    print("1. Configure environment variables in .env file")
    print("2. Start Redis server: redis-server")
    print("3. Start Celery services: ./start_celery.sh")
    print("4. Test manually via admin API endpoints")

if __name__ == "__main__":
    main()
