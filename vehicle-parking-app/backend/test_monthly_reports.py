#!/usr/bin/env python3
"""
Test script for monthly reports functionality
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5004"
ADMIN_TOKEN = "your_admin_token_here"  # You'll need to get this from login

def test_without_auth():
    """Test monthly reports without authentication (should fail)"""
    print("🔒 Testing monthly reports without authentication...")
    
    response = requests.post(f"{BASE_URL}/api/admin/test-monthly-reports")
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.text[:200]}...")  # Show first 200 chars
    else:
        print(f"Response: {response.json()}")
    print()

def test_preview_report():
    """Test monthly report preview for user ID 1"""
    print("📋 Testing monthly report preview...")
    
    # Try without auth first
    response = requests.get(f"{BASE_URL}/api/admin/preview-monthly-report/1")
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Authentication required (as expected)")
    elif response.status_code != 200:
        print(f"Response: {response.text[:200]}...")
    print()

def test_monthly_reports_sync():
    """Test monthly reports synchronously"""
    print("📊 Testing monthly reports (sync) - Current month...")
    
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    data = {
        "month": current_month,
        "year": current_year
    }
    
    # Test without auth
    response = requests.post(
        f"{BASE_URL}/api/admin/test-monthly-reports",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.text[:200]}...")
    else:
        print(f"Response: {response.json()}")
    print()

def test_monthly_reports_specific_user():
    """Test monthly reports for a specific user"""
    print("👤 Testing monthly reports for specific user...")
    
    data = {
        "month": 7,  # July
        "year": 2025,
        "user_id": 1
    }
    
    response = requests.post(
        f"{BASE_URL}/api/admin/test-monthly-reports",
        json=data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.text[:200]}...")
    else:
        print(f"Response: {response.json()}")
    print()

def test_get_users():
    """Test getting all users to see what's available"""
    print("👥 Getting list of users...")
    
    response = requests.get(f"{BASE_URL}/api/admin/users")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        users = response.json()
        print(f"Found {len(users)} users")
        for user in users[:3]:  # Show first 3 users
            print(f"  - ID: {user.get('id')}, Username: {user.get('username')}, Email: {user.get('email')}")
    elif response.status_code == 401:
        print("✅ Authentication required (as expected)")
    else:
        print(f"Response: {response.text[:200]}...")
    print()

def main():
    """Run all tests"""
    print("🚗 Monthly Reports Testing Suite")
    print("=" * 50)
    
    # Test basic functionality
    test_without_auth()
    test_get_users()
    test_preview_report()
    test_monthly_reports_sync()
    test_monthly_reports_specific_user()
    
    print("✅ Testing completed!")
    print("\nNote: Most tests will fail with 401 Unauthorized because admin authentication is required.")
    print("To test with authentication, you would need to:")
    print("1. Login as admin to get a JWT token")
    print("2. Add the token to request headers: {'Authorization': 'Bearer <token>'}")

if __name__ == "__main__":
    main()
