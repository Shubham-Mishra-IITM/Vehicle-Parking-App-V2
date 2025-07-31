#!/usr/bin/env python3

import requests
import json

# Test the analytics endpoint
def test_analytics():
    # First, login as admin to get a token
    login_url = "http://127.0.0.1:5004/api/auth/login"
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        print("🔐 Logging in as admin...")
        login_response = requests.post(login_url, json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            response_data = login_response.json()
            print(f"Login response: {response_data}")
            token = response_data.get('access_token') or response_data.get('token')
            print(f"✅ Login successful, token received: {token[:20]}..." if token else "❌ No token found!")
            
            if not token:
                print("❌ No token in login response!")
                return
            
            # Test analytics endpoint
            analytics_url = "http://127.0.0.1:5004/api/admin/analytics"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            print("📊 Testing analytics endpoint...")
            analytics_response = requests.get(analytics_url, headers=headers)
            print(f"Analytics status: {analytics_response.status_code}")
            
            if analytics_response.status_code == 200:
                data = analytics_response.json()
                print("✅ Analytics data received successfully!")
                print(f"Parking status: {data.get('parking_status', {})}")
                print(f"Summary stats: {data.get('summary_stats', {})}")
            else:
                print(f"❌ Analytics failed: {analytics_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_analytics()
