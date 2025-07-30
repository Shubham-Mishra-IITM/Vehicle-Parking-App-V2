#!/usr/bin/env python3
"""
CSV Export Testing Tool
Test the user-triggered CSV export functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5004"

def login_user(username, password):
    """Login as user and get JWT token"""
    print(f"🔐 Logging in as user: {username}")
    
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

def trigger_csv_export(token):
    """Trigger CSV export job"""
    print("\n📊 Triggering CSV export...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/api/user/export-csv",
        headers=headers
    )
    
    if response.status_code == 202:
        result = response.json()
        print("✅ CSV export job started!")
        print(f"📋 Message: {result.get('message')}")
        print(f"🔄 Task ID: {result.get('task_id')}")
        print(f"⏱️ Estimated time: {result.get('estimated_time')}")
        return result.get('task_id')
    else:
        print(f"❌ Failed to start export: {response.text}")
        return None

def check_export_status(token, task_id):
    """Check export job status"""
    print(f"\n🔍 Checking export status for task: {task_id}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/user/export-status/{task_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"📊 Status: {result.get('status')}")
        print(f"🔄 State: {result.get('state')}")
        print(f"📈 Progress: {result.get('progress', 0)}%")
        print(f"💬 Message: {result.get('message', 'N/A')}")
        
        if result.get('state') == 'SUCCESS':
            print(f"📁 Filename: {result.get('filename')}")
            print(f"📊 Records: {result.get('records_count')}")
            print(f"🔗 Download URL: {result.get('download_url')}")
            return True, result
        elif result.get('state') == 'FAILURE':
            print(f"❌ Error: {result.get('error')}")
            return False, result
        else:
            return None, result  # Still in progress
    else:
        print(f"❌ Failed to check status: {response.text}")
        return False, None

def download_csv_file(token, filename):
    """Download the CSV file"""
    if not filename:
        print("❌ No filename provided")
        return False
    
    print(f"\n📥 Downloading CSV file: {filename}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        f"{BASE_URL}/api/user/download-csv/{filename}",
        headers=headers
    )
    
    if response.status_code == 200:
        # Save the file locally
        local_filename = f"downloaded_{filename}"
        with open(local_filename, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ File downloaded successfully: {local_filename}")
        print(f"📊 File size: {len(response.content)} bytes")
        
        # Show first few lines of the CSV
        try:
            with open(local_filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()[:5]  # First 5 lines
                print(f"\n📋 CSV Preview (first 5 lines):")
                for i, line in enumerate(lines, 1):
                    print(f"  {i}: {line.strip()}")
        except Exception as e:
            print(f"⚠️ Could not preview file: {e}")
        
        return True
    else:
        print(f"❌ Failed to download file: {response.text}")
        return False

def test_full_export_workflow(username, password):
    """Test the complete CSV export workflow"""
    print("=" * 60)
    print("🧪 CSV EXPORT WORKFLOW TEST")
    print("=" * 60)
    
    # Step 1: Login
    token = login_user(username, password)
    if not token:
        return False
    
    # Step 2: Trigger export
    task_id = trigger_csv_export(token)
    if not task_id:
        return False
    
    # Step 3: Poll status until completion
    max_attempts = 30  # 30 attempts with 2-second intervals = 1 minute max
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\n🔄 Status check attempt {attempt}/{max_attempts}")
        
        is_complete, result = check_export_status(token, task_id)
        
        if is_complete is True:
            # Success - try to download
            filename = result.get('filename')
            if filename:
                return download_csv_file(token, filename)
            else:
                print("❌ No filename in successful result")
                return False
        elif is_complete is False:
            # Failed
            return False
        else:
            # Still in progress
            print("⏳ Job still in progress, waiting 2 seconds...")
            time.sleep(2)
    
    print("❌ Export job timed out")
    return False

def main():
    """Main test function"""
    print("🧪 CSV EXPORT TESTING TOOL")
    print("=" * 50)
    
    # Test users
    test_users = [
        {"username": "abc", "password": "123"},
        {"username": "testuser", "password": "password123"}
    ]
    
    for user in test_users:
        print(f"\n🎯 Testing CSV export for user: {user['username']}")
        success = test_full_export_workflow(user['username'], user['password'])
        
        if success:
            print(f"✅ CSV export test PASSED for {user['username']}")
        else:
            print(f"❌ CSV export test FAILED for {user['username']}")
        
        print("-" * 50)

if __name__ == "__main__":
    main()
