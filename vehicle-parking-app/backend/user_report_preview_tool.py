#!/usr/bin/env python3
"""
User Monthly Report Preview Tool
This tool allows admins to preview what specific users will receive in their monthly reports
"""

import requests
import json
from datetime import datetime
import webbrowser
import os

# Configuration
BASE_URL = "http://localhost:5004"

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

def get_all_users(token):
    """Get list of all users"""
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(f"{BASE_URL}/api/admin/users", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to get users: {response.text}")
        return []

def preview_user_report(token, user_id, month=None, year=None):
    """Preview monthly report for a specific user"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Use current month/year if not specified
    month = month or datetime.now().month
    year = year or datetime.now().year
    
    response = requests.get(
        f"{BASE_URL}/api/admin/preview-monthly-report/{user_id}?month={month}&year={year}",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.text
    else:
        print(f"❌ Failed to preview report: {response.text}")
        return None

def send_test_report_to_user(token, user_id, month=None, year=None):
    """Send actual test report to a specific user"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    month = month or datetime.now().month
    year = year or datetime.now().year
    
    data = {
        "month": month,
        "year": year,
        "user_id": user_id
    }
    
    response = requests.post(
        f"{BASE_URL}/api/admin/test-monthly-reports",
        json=data,
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to send test report: {response.text}")
        return None

def save_and_open_preview(html_content, user_info, month, year):
    """Save HTML preview to file and open in browser"""
    filename = f"user_report_preview_{user_info['username']}_{month}_{year}.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"💾 Report saved as: {filename}")
    
    # Try to open in default browser
    try:
        file_path = os.path.abspath(filename)
        webbrowser.open(f"file://{file_path}")
        print(f"🌐 Opening report in browser...")
    except Exception as e:
        print(f"⚠️ Could not open browser: {e}")
    
    return filename

def main():
    """Interactive tool to preview user reports"""
    print("📊 User Monthly Report Preview Tool")
    print("=" * 50)
    
    # Login
    token = login_admin()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Get users
    print("\n👥 Fetching users...")
    users = get_all_users(token)
    if not users:
        print("❌ No users found")
        return
    
    print(f"✅ Found {len(users)} users:")
    for i, user in enumerate(users, 1):
        print(f"  {i}. {user['username']} ({user['email']}) - ID: {user['id']}")
    
    print("\n🎯 What would you like to do?")
    print("1. Preview report for specific user")
    print("2. Send test email to specific user")
    print("3. Preview reports for all users")
    print("4. Test with different month/year")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            user_choice = int(input(f"Enter user number (1-{len(users)}): ")) - 1
            selected_user = users[user_choice]
            
            print(f"\n📋 Previewing report for {selected_user['username']}...")
            html_content = preview_user_report(token, selected_user['id'])
            
            if html_content:
                filename = save_and_open_preview(
                    html_content, 
                    selected_user, 
                    datetime.now().month, 
                    datetime.now().year
                )
                print(f"✅ Preview generated successfully!")
                print(f"📄 File: {filename}")
                print(f"📊 Content length: {len(html_content)} characters")
        
        elif choice == "2":
            user_choice = int(input(f"Enter user number (1-{len(users)}): ")) - 1
            selected_user = users[user_choice]
            
            print(f"\n📧 Sending test email to {selected_user['username']} ({selected_user['email']})...")
            result = send_test_report_to_user(token, selected_user['id'])
            
            if result:
                print("✅ Test email sent successfully!")
                print(f"📊 Result: {result}")
            
        elif choice == "3":
            print(f"\n📋 Generating previews for all {len(users)} users...")
            for user in users[:5]:  # Limit to first 5 users
                print(f"\n👤 Processing {user['username']}...")
                html_content = preview_user_report(token, user['id'])
                
                if html_content:
                    filename = save_and_open_preview(
                        html_content, 
                        user, 
                        datetime.now().month, 
                        datetime.now().year
                    )
                    print(f"✅ Generated: {filename}")
        
        elif choice == "4":
            month = int(input("Enter month (1-12): "))
            year = int(input("Enter year (e.g., 2025): "))
            user_choice = int(input(f"Enter user number (1-{len(users)}): ")) - 1
            selected_user = users[user_choice]
            
            print(f"\n📋 Previewing {selected_user['username']}'s report for {month}/{year}...")
            html_content = preview_user_report(token, selected_user['id'], month, year)
            
            if html_content:
                filename = save_and_open_preview(html_content, selected_user, month, year)
                print(f"✅ Preview generated successfully!")
        
        else:
            print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
