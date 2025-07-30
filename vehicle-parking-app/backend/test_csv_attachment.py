#!/usr/bin/env python3
"""
CSV Attachment Test for MailHog
===============================
Tests CSV file attachment specifically
"""

import os
import tempfile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from config import Config

def test_csv_attachment():
    print('📎 Testing CSV Attachment in MailHog')
    print('=' * 40)
    
    try:
        # Create a test CSV file with actual content
        csv_content = """Reservation ID,Parking Lot,Vehicle Number,Date,Cost
1,Shopping Mall,ABC123,2025-07-30,15.50
2,Airport Terminal,XYZ789,2025-07-30,25.00
3,University Campus,DEF456,2025-07-30,10.00"""
        
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            temp_file_path = f.name
        
        filename = 'test_parking_history.csv'
        
        print(f'📁 Created test CSV: {temp_file_path}')
        print(f'📊 File size: {os.path.getsize(temp_file_path)} bytes')
        print()
        
        # Create email with attachment
        msg = MIMEMultipart()
        msg['From'] = Config.MAIL_DEFAULT_SENDER or 'test@parkingapp.local'
        msg['To'] = 'abc@hotmail.com'
        msg['Subject'] = '📎 Test CSV Attachment - Parking History'
        
        # Email body
        body = """Hi there!

This is a test email with a CSV attachment.

📊 The attached CSV file contains sample parking history data.
📎 File name: test_parking_history.csv
💾 File type: text/csv

If you can see this attachment in MailHog, then CSV attachments are working correctly!

Best regards,
Parking App Team"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        print('📎 Adding CSV attachment...')
        
        # Add CSV file as attachment - using proper MIME type for CSV
        with open(temp_file_path, 'rb') as attachment:
            part = MIMEBase('text', 'csv')  # Better MIME type for CSV
            part.set_payload(attachment.read())
        
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{filename}"'  # Proper quoting
        )
        msg.attach(part)
        
        print('📤 Sending email with attachment...')
        
        # Send email using the same approach as the working direct email test
        try:
            server = smtplib.SMTP()
            server.connect(Config.MAIL_SERVER, Config.MAIL_PORT)
            
            # Send the message
            server.send_message(msg)
            server.quit()
            
        except Exception as smtp_error:
            print(f'SMTP Error: {smtp_error}')
            raise
        
        print('✅ Email with CSV attachment sent!')
        print('🌐 Check MailHog at: http://localhost:8025')
        print('📧 Look for: "📎 Test CSV Attachment - Parking History"')
        print('📎 The email should have test_parking_history.csv attached')
        
        # Clean up
        os.unlink(temp_file_path)
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        
        # Clean up on error
        if 'temp_file_path' in locals():
            try:
                os.unlink(temp_file_path)
            except:
                pass

if __name__ == '__main__':
    test_csv_attachment()
