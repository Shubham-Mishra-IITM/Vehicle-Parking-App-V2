#!/usr/bin/env python3
"""
Direct MailHog Email Test
========================
Tests email sending directly to MailHog without CSV export
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

def test_direct_email():
    print('📧 Direct MailHog Email Test')
    print('=' * 30)
    
    try:
        # Check configuration
        print(f'MAIL_SERVER: {Config.MAIL_SERVER}')
        print(f'MAIL_PORT: {Config.MAIL_PORT}')
        print(f'MAIL_USE_TLS: {Config.MAIL_USE_TLS}')
        print(f'MAIL_DEFAULT_SENDER: {Config.MAIL_DEFAULT_SENDER}')
        print()
        
        if not Config.MAIL_SERVER:
            print('❌ MAIL_SERVER not configured')
            return
        
        # Create test email
        msg = MIMEMultipart()
        msg['From'] = Config.MAIL_DEFAULT_SENDER or 'test@parkingapp.local'
        msg['To'] = 'user@test.com'
        msg['Subject'] = '🧪 MailHog Test Email from Parking App'
        
        body = """
Hi there!

This is a test email from your Vehicle Parking App to verify MailHog integration.

✅ If you can see this email in MailHog (http://localhost:8025), then email sending is working correctly!

🎯 Next step: CSV export emails should work the same way.

Best regards,
Parking App Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email to MailHog
        print('📤 Sending test email to MailHog...')
        
        with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
            if Config.MAIL_USE_TLS:
                server.starttls()
            
            # MailHog doesn't require authentication
            if Config.MAIL_USERNAME:
                server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD or '')
            
            server.send_message(msg)
        
        print('✅ Email sent successfully!')
        print('🌐 Check MailHog at: http://localhost:8025')
        print('📧 Look for: "🧪 MailHog Test Email from Parking App"')
        
    except Exception as e:
        print(f'❌ Email sending failed: {e}')
        print('🔍 Troubleshooting:')
        print('   1. Is MailHog running? docker ps --filter name=mailhog')
        print('   2. Is port 1025 accessible? telnet localhost 1025')
        print('   3. Check MailHog logs: docker logs mailhog')

if __name__ == '__main__':
    test_direct_email()
