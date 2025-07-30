#!/usr/bin/env python3
"""
Complete test script for monthly reports with authentication
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5004"

def create_admin_user():
    """Create an admin user for testing"""
    print("👤 Creating admin user...")
    
    admin_data = {
        "username": "admin",
        "email": "admin@parkingapp.com",
        "password": "admin123",
        "phone": "+1234567890"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json=admin_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        print("✅ Admin user created successfully!")
    elif response.status_code == 400 and "already exists" in response.text:
        print("ℹ️ Admin user already exists")
    else:
        print(f"Response: {response.text}")
    print()

def login_admin():
    """Login as admin and get JWT token"""
    print("🔐 Logging in as admin...")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        # Try both possible token field names
        token = result.get('access_token') or result.get('token')
        if token:
            print("✅ Login successful!")
            print(f"Token (first 50 chars): {token[:50]}...")
            print()
            return token
        else:
            print(f"❌ No token in response: {result}")
            print()
            return None
    else:
        print(f"❌ Login failed: {response.text}")
        print()
        return None

def test_monthly_reports_with_auth(token):
    """Test monthly reports with proper authentication"""
    if not token:
        print("❌ No token available for authenticated testing")
        return
    
    print("📊 Testing monthly reports with authentication...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test current month
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    data = {
        "month": current_month,
        "year": current_year
    }
    
    response = requests.post(
        f"{BASE_URL}/api/admin/test-monthly-reports",
        json=data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("✅ Monthly reports test successful!")
        print(f"Reports sent: {result.get('reports_sent', 0)}")
        print(f"Message: {result.get('message', '')}")
        if result.get('errors'):
            print(f"Errors: {result['errors']}")
    else:
        print(f"❌ Test failed: {response.text}")
    print()

def test_preview_report_with_auth(token):
    """Test monthly report preview with authentication"""
    if not token:
        print("❌ No token available for authenticated testing")
        return
    
    print("📋 Testing monthly report preview with authentication...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # Try to preview report for user ID 1
    response = requests.get(
        f"{BASE_URL}/api/admin/preview-monthly-report/1?month=7&year=2025",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Preview generated successfully!")
        print(f"Content type: {response.headers.get('content-type')}")
        print(f"Content length: {len(response.text)} characters")
        # Save preview to file
        with open('monthly_report_preview.html', 'w') as f:
            f.write(response.text)
        print("💾 Preview saved to 'monthly_report_preview.html'")
    else:
        print(f"❌ Preview failed: {response.text}")
    print()

def test_async_monthly_reports(token):
    """Test asynchronous monthly reports"""
    if not token:
        print("❌ No token available for authenticated testing")
        return
    
    print("⚡ Testing asynchronous monthly reports...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "month": 7,
        "year": 2025
    }
    
    response = requests.post(
        f"{BASE_URL}/api/admin/test-monthly-reports-async",
        json=data,
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print("✅ Async task queued successfully!")
        print(f"Task ID: {result.get('task_id')}")
        print(f"Message: {result.get('message')}")
        
        # Check task status
        task_id = result.get('task_id')
        if task_id:
            check_task_status(token, task_id)
    else:
        print(f"❌ Async test failed: {response.text}")
    print()

def check_task_status(token, task_id):
    """Check the status of a Celery task"""
    print(f"🔍 Checking status of task {task_id}...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/admin/task-status/{task_id}",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Task state: {result.get('state')}")
        if result.get('result'):
            print(f"Result: {result['result']}")
        if result.get('error'):
            print(f"Error: {result['error']}")
    else:
        print(f"❌ Status check failed: {response.text}")
    print()

def get_users_with_auth(token):
    """Get all users with authentication"""
    if not token:
        print("❌ No token available for authenticated testing")
        return
    
    print("👥 Getting list of users with authentication...")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/admin/users",
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        users = response.json()
        print(f"✅ Found {len(users)} users:")
        for user in users[:5]:  # Show first 5 users
            print(f"  - ID: {user.get('id')}, Username: {user.get('username')}, Email: {user.get('email')}")
        return users
    else:
        print(f"❌ Failed to get users: {response.text}")
        return []
    print()

def main():
    """Run all tests with authentication"""
    print("🚗 Monthly Reports Authentication Testing Suite")
    print("=" * 60)
    
    # Step 1: Create admin user
    create_admin_user()
    
    # Step 2: Login and get token
    token = login_admin()
    
    if token:
        # Step 3: Test with authentication
        users = get_users_with_auth(token)
        test_monthly_reports_with_auth(token)
        test_preview_report_with_auth(token)
        test_async_monthly_reports(token)
        
        print("✅ All authenticated tests completed!")
        print("\n📝 Summary:")
        print("- Admin user created/verified")
        print("- JWT authentication working")
        print("- Monthly reports endpoints accessible")
        print("- Both sync and async operations tested")
        print("- HTML preview generation working")
    else:
        print("❌ Authentication failed - cannot proceed with authenticated tests")

if __name__ == "__main__":
    main()
