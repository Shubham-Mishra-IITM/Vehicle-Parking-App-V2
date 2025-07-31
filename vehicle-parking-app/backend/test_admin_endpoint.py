#!/usr/bin/env python3
import requests
import json

def test_admin_endpoint():
    base_url = "http://localhost:5004"
    
    # First login to get admin token
    print("🔐 Attempting admin login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        login_response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Login response status: {login_response.status_code}")
        print(f"Login response: {login_response.text}")
        
        if login_response.status_code == 200:
            token = login_response.json().get('token')
            if token:
                print(f"✅ Got admin token: {token[:50]}...")
                
                # Now test the parking spots endpoint
                print("\n🚗 Testing parking spots status endpoint...")
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                
                spots_response = requests.get(
                    f"{base_url}/api/admin/parking-spots/status",
                    headers=headers
                )
                
                print(f"Spots response status: {spots_response.status_code}")
                print(f"Spots response: {spots_response.text}")
                
            else:
                print("❌ No token in login response")
        else:
            print(f"❌ Login failed with status {login_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_admin_endpoint()
