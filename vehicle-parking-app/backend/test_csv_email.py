#!/usr/bin/env python3
"""
Test CSV Export Email Functionality
===================================
Tests the specific email sending function used by CSV export
"""

import os
import tempfile
from tasks.export_csv import send_csv_export_email
from models.user import User
from config import Config

def test_csv_export_email():
    print('📊 Testing CSV Export Email Function')
    print('=' * 40)
    
    try:
        # Check email configuration
        print('🔧 Email Configuration:')
        print(f'  MAIL_SERVER: {Config.MAIL_SERVER}')
        print(f'  MAIL_PORT: {Config.MAIL_PORT}')
        print(f'  MAIL_USE_TLS: {Config.MAIL_USE_TLS}')
        print(f'  MAIL_DEFAULT_SENDER: {Config.MAIL_DEFAULT_SENDER}')
        print()
        
        # Create a dummy user object
        class DummyUser:
            def __init__(self):
                self.username = 'abc'
                self.email = 'abc@hotmail.com'
        
        user = DummyUser()
        
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write('Test CSV Content\\nReservation ID,User,Date\\n1,abc,2025-07-30')
            temp_file_path = f.name
        
        filename = 'test_export.csv'
        
        print(f'👤 Testing with user: {user.username} ({user.email})')
        print(f'📁 Test file: {temp_file_path}')
        print()
        
        print('📤 Sending CSV export email...')
        
        # Call the actual email sending function
        send_csv_export_email(user, temp_file_path, filename)
        
        print('✅ Email sent successfully!')
        print('🌐 Check MailHog at: http://localhost:8025')
        print('📧 Look for email to: abc@hotmail.com')
        print('📎 Should have CSV attachment')
        
        # Clean up
        os.unlink(temp_file_path)
        
    except Exception as e:
        print(f'❌ Email sending failed: {e}')
        import traceback
        print('🔍 Full error:')
        traceback.print_exc()
        
        # Clean up on error
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass

if __name__ == '__main__':
    test_csv_export_email()
