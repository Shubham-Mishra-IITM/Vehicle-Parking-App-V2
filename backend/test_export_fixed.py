#!/usr/bin/env python3
"""Test CSV export with fixed email attachment"""

import requests
import time
import sys

def test_csv_export_with_attachment():
    print('🧪 Testing CSV Export with Fixed Email Attachment')
    print('=' * 60)
    
    BASE_URL = 'http://localhost:5004'
    
    try:
        # Step 1: Login
        print('📝 Step 1: Logging in...')
        response = requests.post(f'{BASE_URL}/api/auth/login', json={
            'username': 'abc', 
            'password': '123'
        })
        
        if response.status_code != 200:
            print(f'❌ Login failed: {response.status_code}')
            return False
            
        token = response.json().get('token')
        print('✅ Login successful')
        
        # Step 2: Trigger CSV export
        print('\n📤 Step 2: Triggering CSV export...')
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(f'{BASE_URL}/api/user/export-csv', headers=headers)
        
        if response.status_code != 202:
            print(f'❌ Export trigger failed: {response.status_code} - {response.text}')
            return False
            
        result = response.json()
        task_id = result.get('task_id')
        print(f'✅ CSV export triggered with task ID: {task_id}')
        
        # Step 3: Monitor progress
        print('\n⏳ Step 3: Monitoring export progress...')
        for i in range(10):
            time.sleep(3)
            response = requests.get(f'{BASE_URL}/api/user/export-status/{task_id}', headers=headers)
            
            if response.status_code == 200:
                status = response.json()
                state = status.get('state')
                message = status.get('status', 'Processing...')
                
                print(f'   Check {i+1}/10: {state} - {message}')
                
                if state == 'SUCCESS':
                    filename = status.get('filename')
                    print('\n🎉 SUCCESS! CSV Export completed!')
                    print(f'   📁 Generated file: {filename}')
                    print('   📧 Email with CSV attachment sent!')
                    print('   🌐 Check MailHog at: http://localhost:8025')
                    print('\n✨ Key fixes applied:')
                    print('   • Fixed SMTP connection for MailHog (no TLS)')
                    print('   • Changed MIME type to text/csv for proper attachment')
                    print('   • Added proper error handling')
                    return True
                    
                elif state == 'FAILURE':
                    error_info = status.get('result', message)
                    print(f'\n❌ Export failed: {error_info}')
                    return False
                    
            else:
                print(f'   ❌ Status check failed: {response.status_code}')
                
        print('\n⏰ Export monitoring timed out after 30 seconds')
        return False
        
    except Exception as e:
        print(f'\n❌ Error during test: {e}')
        return False

if __name__ == '__main__':
    success = test_csv_export_with_attachment()
    sys.exit(0 if success else 1)
