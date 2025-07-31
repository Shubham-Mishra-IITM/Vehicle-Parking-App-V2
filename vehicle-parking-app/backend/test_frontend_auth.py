#!/usr/bin/env python3
"""
Test script to verify frontend authentication by simulating the exact request flow
"""
import requests
import json

def test_frontend_auth():
    # Test the exact flow that frontend uses
    base_url = "http://localhost:8081"  # Frontend URL
    
    print("🔍 Testing frontend authentication flow...")
    
    # Step 1: Test login through frontend proxy
    login_data = {
        "username": "admin", 
        "password": "admin123"
    }
    
    print("📝 Logging in through frontend proxy...")
    try:
        login_response = requests.post(
            f"{base_url}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            response_data = login_response.json()
            token = response_data.get('token')
            print(f"✅ Login successful, token received: {token[:20]}..." if token else "❌ No token!")
            
            # Step 2: Test analytics endpoint through frontend proxy
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            print("📊 Testing analytics through frontend proxy...")
            analytics_response = requests.get(
                f"{base_url}/api/admin/analytics",
                headers=headers
            )
            
            print(f"Analytics status: {analytics_response.status_code}")
            
            if analytics_response.status_code == 200:
                data = analytics_response.json()
                print("✅ Analytics successful!")
                print(f"Parking status: {data.get('parking_status', {})}")
            else:
                print(f"❌ Analytics failed: {analytics_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection failed - is frontend running on port 8081? Error: {e}")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_frontend_auth()
