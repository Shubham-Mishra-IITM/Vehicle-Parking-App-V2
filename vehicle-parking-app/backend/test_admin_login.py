#!/usr/bin/env python3
import requests
import json

def test_admin_login():
    url = "http://localhost:5004/api/auth/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        print("🔍 Testing admin login...")
        response = requests.post(url, json=data)
        print(f"✅ Status Code: {response.status_code}")
        print(f"📄 Response: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"🎉 Login successful!")
            print(f"👤 User: {response_data['user']['username']}")
            print(f"🔑 Role: {response_data['user']['role']}")
            print(f"🎫 Token: {response_data['token'][:50]}...")
            
            # Test admin dashboard with token
            headers = {"Authorization": f"Bearer {response_data['token']}"}
            dashboard_response = requests.get("http://localhost:5004/api/admin/dashboard", headers=headers)
            print(f"📊 Dashboard Status: {dashboard_response.status_code}")
            if dashboard_response.status_code == 200:
                print(f"📈 Dashboard Data: {dashboard_response.json()}")
            else:
                print(f"❌ Dashboard Error: {dashboard_response.text}")
        else:
            print(f"❌ Login failed: {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_admin_login()
