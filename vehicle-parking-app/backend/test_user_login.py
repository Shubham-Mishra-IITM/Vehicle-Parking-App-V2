#!/usr/bin/env python3
import requests
import json

def test_user_login():
    # First, let's check if there are any regular users
    url = "http://localhost:5004/debug-db"
    
    try:
        print("🔍 Checking available users...")
        response = requests.get(url)
        if response.status_code == 200:
            users = response.json().get('users', [])
            print(f"👥 Available users: {users}")
            
            # Find a non-admin user
            regular_users = [u for u in users if u['role'] != 'admin']
            if regular_users:
                test_user = regular_users[0]
                print(f"🎯 Testing with user: {test_user['username']}")
                
                # Try to login (we'll need to know the password)
                login_url = "http://localhost:5004/api/auth/login"
                # Common passwords to try
                passwords = ['password', 'user123', '123456', 'password123']
                
                for password in passwords:
                    login_data = {
                        "username": test_user['username'],
                        "password": password
                    }
                    
                    print(f"🔐 Trying password: {password}")
                    login_response = requests.post(login_url, json=login_data)
                    
                    if login_response.status_code == 200:
                        print(f"✅ Login successful with password: {password}")
                        response_data = login_response.json()
                        token = response_data['token']
                        
                        # Test user profile endpoint
                        headers = {"Authorization": f"Bearer {token}"}
                        profile_response = requests.get("http://localhost:5004/api/user/profile", headers=headers)
                        print(f"👤 Profile Status: {profile_response.status_code}")
                        if profile_response.status_code == 200:
                            print(f"📄 Profile Data: {profile_response.json()}")
                        else:
                            print(f"❌ Profile Error: {profile_response.text}")
                        
                        # Test user dashboard
                        dashboard_response = requests.get("http://localhost:5004/api/user/dashboard", headers=headers)
                        print(f"📊 Dashboard Status: {dashboard_response.status_code}")
                        if dashboard_response.status_code == 200:
                            print(f"📈 Dashboard Data Keys: {list(dashboard_response.json().keys())}")
                        else:
                            print(f"❌ Dashboard Error: {dashboard_response.text}")
                        
                        return True
                    else:
                        print(f"❌ Login failed with {password}: {login_response.text}")
                
                print(f"⚠️ Could not find correct password for user {test_user['username']}")
                return False
            else:
                print("⚠️ No regular users found. Let's create one...")
                # Register a test user
                register_url = "http://localhost:5004/api/auth/register"
                register_data = {
                    "username": "testuser",
                    "email": "test@example.com",
                    "password": "password123",
                    "phone_number": "+1234567891"
                }
                
                register_response = requests.post(register_url, json=register_data)
                print(f"📝 Registration Status: {register_response.status_code}")
                if register_response.status_code == 201:
                    print("✅ Test user created successfully!")
                    
                    # Now try to login with the new user
                    login_data = {
                        "username": "testuser",
                        "password": "password123"
                    }
                    
                    login_response = requests.post(login_url, json=login_data)
                    if login_response.status_code == 200:
                        print("✅ Login successful with new user!")
                        response_data = login_response.json()
                        token = response_data['token']
                        
                        # Test user profile endpoint
                        headers = {"Authorization": f"Bearer {token}"}
                        profile_response = requests.get("http://localhost:5004/api/user/profile", headers=headers)
                        print(f"👤 Profile Status: {profile_response.status_code}")
                        if profile_response.status_code == 200:
                            print(f"📄 Profile Data: {profile_response.json()}")
                        else:
                            print(f"❌ Profile Error: {profile_response.text}")
                        
                        return True
                else:
                    print(f"❌ Registration failed: {register_response.text}")
                    return False
        
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

if __name__ == "__main__":
    test_user_login()
