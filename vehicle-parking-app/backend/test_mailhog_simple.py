#!/usr/bin/env python3
"""Simple email test for MailHog"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_mailhog_simple():
    print('🧪 Testing MailHog Email Sending')
    print('=' * 50)
    
    # MailHog configuration
    smtp_server = 'localhost'
    smtp_port = 1025
    sender_email = 'test@parkingapp.local'
    recipient_email = 'abc@example.com'
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = 'CSV Export Test - Vehicle Parking App'
        
        # Email body
        body = """
Hello!

This is a test email from the Vehicle Parking App CSV export functionality.

If you can see this email in MailHog, then the email system is working correctly!

Best regards,
Vehicle Parking App
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to MailHog SMTP server
        print(f'📧 Connecting to MailHog at {smtp_server}:{smtp_port}...')
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        # Send email
        print(f'📤 Sending test email to {recipient_email}...')
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        
        print('✅ Email sent successfully!')
        print('🌐 Check MailHog at: http://localhost:8025')
        
        return True
        
    except Exception as e:
        print(f'❌ Email sending failed: {e}')
        return False

def test_csv_attachment():
    print('\n🧪 Testing CSV Attachment Email')
    print('=' * 50)
    
    # Check if a CSV file exists
    csv_path = '/Users/shubham/Desktop/Vehicle_Parking_App_V2/vehicle-parking-app-v2/vehicle-parking-app/backend/exports/parking_history_abc_20250730_184239.csv'
    
    if not os.path.exists(csv_path):
        print(f'❌ CSV file not found: {csv_path}')
        # Create a sample CSV for testing
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        with open(csv_path, 'w') as f:
            f.write('Reservation ID,Parking Lot,Vehicle Number,Date,Time,Duration,Cost\n')
            f.write('1,Downtown Plaza,ABC123,2025-07-30,10:00,2.5,12.50\n')
            f.write('2,Shopping Mall,XYZ789,2025-07-29,14:30,1.0,4.50\n')
        print(f'✅ Created sample CSV file for testing')
    
    try:
        # Create message with attachment
        msg = MIMEMultipart()
        msg['From'] = 'noreply@parkingapp.local'
        msg['To'] = 'abc@example.com'
        msg['Subject'] = 'Your Parking History Export is Ready!'
        
        # Email body
        body = """
Dear abc,

Your parking history export has been completed successfully! 🎉

The attached CSV file contains all your parking reservations with detailed information including:
• Reservation details
• Parking locations  
• Duration and costs
• Timestamps

Please find your complete parking history attached.

Thank you for using Vehicle Parking App!

Best regards,
Vehicle Parking App Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Add CSV attachment
        with open(csv_path, 'rb') as attachment:
            part = MIMEBase('text', 'csv')
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename= parking_history_abc.csv'
        )
        msg.attach(part)
        
        # Send email
        smtp_server = 'localhost'
        smtp_port = 1025
        
        print(f'📧 Connecting to MailHog at {smtp_server}:{smtp_port}...')
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        print(f'📤 Sending CSV attachment email...')
        text = msg.as_string()
        server.sendmail('noreply@parkingapp.local', 'abc@example.com', text)
        server.quit()
        
        print('✅ CSV attachment email sent successfully!')
        print('🌐 Check MailHog at: http://localhost:8025')
        
        return True
        
    except Exception as e:
        print(f'❌ CSV attachment email failed: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # Test basic email
    success1 = test_mailhog_simple()
    
    # Test CSV attachment
    success2 = test_csv_attachment()
    
    if success1 and success2:
        print('\n🎉 All email tests passed!')
        print('📧 Check your MailHog inbox at http://localhost:8025')
    else:
        print('\n❌ Some email tests failed!')
