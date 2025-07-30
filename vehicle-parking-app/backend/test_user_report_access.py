#!/usr/bin/env python3
"""
User Monthly Report Access Test
This demonstrates how users can access their own monthly reports
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5004"

def login_user(username, password):
    """Login as a regular user"""
    print(f"🔐 Logging in as {username}...")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        token = result.get('access_token') or result.get('token')
        if token:
            print("✅ Login successful!")
            return token
        else:
            print(f"❌ No token in response")
            return None
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_user_monthly_report_access():
    """Test how users can access their monthly reports"""
    print("👤 Testing User Monthly Report Access")
    print("=" * 50)
    
    # Try to login as a regular user (you may need to adjust credentials)
    # Let's try with one of the existing users
    token = login_user("testuser", "testpassword")  # You may need to adjust password
    
    if not token:
        print("⚠️ Could not login as regular user. Let's use admin for demonstration.")
        token = login_user("admin", "admin123")
    
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Get monthly report history
    print("\n📋 Testing monthly report history...")
    response = requests.get(f"{BASE_URL}/api/user/monthly-reports/history", headers=headers)
    
    if response.status_code == 200:
        history = response.json()
        print("✅ Report history retrieved successfully!")
        print(f"👤 User: {history['user']}")
        print(f"📊 Total months with activity: {history['total_months']}")
        
        if history['available_reports']:
            print("📅 Available reports:")
            for report in history['available_reports'][:3]:  # Show first 3
                print(f"  - {report['month_name']} {report['year']}: {report['reservation_count']} reservations")
                print(f"    URL: {report['report_url']}")
        else:
            print("ℹ️ No reports available (user has no parking activity)")
    else:
        print(f"❌ Failed to get history: {response.text}")
    
    # Test 2: Get current month report (JSON format)
    print(f"\n📊 Testing current month report (JSON)...")
    response = requests.get(f"{BASE_URL}/api/user/monthly-report", headers=headers)
    
    if response.status_code == 200:
        report = response.json()
        print("✅ Monthly report retrieved successfully!")
        print(f"📅 Month/Year: {report['month']}/{report['year']}")
        print(f"👤 User: {report['user']}")
        data = report['report_data']
        print(f"📊 Total reservations: {data['total_reservations']}")
        print(f"💰 Total spent: ₹{data['total_amount_spent']:.2f}")
        print(f"⏰ Total hours: {data['total_hours_parked']:.1f}h")
    else:
        print(f"❌ Failed to get report: {response.text}")
    
    # Test 3: Get current month report (HTML format)
    print(f"\n🌐 Testing current month report (HTML)...")
    response = requests.get(f"{BASE_URL}/api/user/monthly-report?format=html", headers=headers)
    
    if response.status_code == 200:
        print("✅ HTML report retrieved successfully!")
        print(f"📄 Content type: {response.headers.get('content-type')}")
        print(f"📊 Content length: {len(response.text)} characters")
        
        # Save user's HTML report
        filename = "user_own_report_preview.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"💾 User's report saved as: {filename}")
    else:
        print(f"❌ Failed to get HTML report: {response.text}")
    
    # Test 4: Get specific month report
    print(f"\n📅 Testing specific month report (July 2025, HTML)...")
    response = requests.get(f"{BASE_URL}/api/user/monthly-report?month=7&year=2025&format=html", headers=headers)
    
    if response.status_code == 200:
        print("✅ Specific month report retrieved successfully!")
        filename = "user_july_2025_report.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"💾 July 2025 report saved as: {filename}")
    else:
        print(f"❌ Failed to get specific month report: {response.text}")

if __name__ == "__main__":
    test_user_monthly_report_access()
