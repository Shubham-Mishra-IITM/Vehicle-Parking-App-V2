#!/usr/bin/env python3
import requests
import json

def test_admin_analytics():
    url = "http://localhost:5004/api/auth/login"
    data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        print("🔍 Testing admin analytics...")
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            response_data = response.json()
            token = response_data['token']
            
            # Test analytics endpoint
            headers = {"Authorization": f"Bearer {token}"}
            analytics_response = requests.get("http://localhost:5004/api/admin/analytics", headers=headers)
            print(f"📊 Analytics Status: {analytics_response.status_code}")
            if analytics_response.status_code == 200:
                print(f"📈 Analytics Data Keys: {list(analytics_response.json().keys())}")
                analytics_data = analytics_response.json()
                print(f"🚗 Parking Status: {analytics_data.get('parking_status', 'N/A')}")
                print(f"💰 Daily Revenue: {len(analytics_data.get('daily_revenue', {}).get('dates', []))} days")
            else:
                print(f"❌ Analytics Error: {analytics_response.text}")
            
            # Test public stats endpoint
            public_response = requests.get("http://localhost:5004/api/public/stats")
            print(f"🌍 Public Stats Status: {public_response.status_code}")
            if public_response.status_code == 200:
                print(f"📊 Public Stats: {public_response.json()}")
            else:
                print(f"❌ Public Stats Error: {public_response.text}")
                
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_admin_analytics()
