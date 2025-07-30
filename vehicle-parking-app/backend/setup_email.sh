#!/bin/bash

# Email Configuration Setup Script for Parking App V2
# ===================================================

echo "🚗 Vehicle Parking App V2 - Email Configuration Setup"
echo "======================================================"
echo ""

# Check if .env file exists
if [ -f ".env" ]; then
    echo "✅ Found existing .env file"
else
    echo "📄 Creating new .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file"
fi

echo ""
echo "📧 Email Provider Options:"
echo "1. Gmail (Recommended for Production)"
echo "2. Outlook/Hotmail" 
echo "3. Yahoo Mail"
echo "4. MailHog (Local Testing - Recommended for Development)"
echo "5. Custom SMTP Server"
echo ""

read -p "Choose your email provider (1-5): " choice

case $choice in
    1)
        echo "📧 Setting up Gmail SMTP..."
        MAIL_SERVER="smtp.gmail.com"
        MAIL_PORT="587"
        USE_CREDENTIALS=true
        ;;
    2)
        echo "📧 Setting up Outlook SMTP..."
        MAIL_SERVER="smtp-mail.outlook.com"
        MAIL_PORT="587"
        USE_CREDENTIALS=true
        ;;
    3)
        echo "📧 Setting up Yahoo SMTP..."
        MAIL_SERVER="smtp.mail.yahoo.com"
        MAIL_PORT="587"
        USE_CREDENTIALS=true
        ;;
    4)
        echo "📧 Setting up MailHog (Local Testing)..."
        MAIL_SERVER="localhost"
        MAIL_PORT="1025"
        USE_CREDENTIALS=false
        echo ""
        echo "🐳 Starting MailHog with Docker..."
        if command -v docker &> /dev/null; then
            docker run -d --name mailhog -p 1025:1025 -p 8025:8025 mailhog/mailhog 2>/dev/null || echo "ℹ️ MailHog container may already be running"
            echo "✅ MailHog started! Web interface: http://localhost:8025"
        else
            echo "⚠️ Docker not found. Please install MailHog manually or use Docker."
            echo "   Install: brew install mailhog (macOS) or download from GitHub"
            echo "   Run: mailhog"
        fi
        ;;
    5)
        read -p "Enter SMTP server: " MAIL_SERVER
        read -p "Enter SMTP port (usually 587): " MAIL_PORT
        USE_CREDENTIALS=true
        ;;
    *)
        echo "❌ Invalid choice. Defaulting to MailHog..."
        MAIL_SERVER="localhost"
        MAIL_PORT="1025"
        USE_CREDENTIALS=false
        ;;
esac

echo ""

if [ "$USE_CREDENTIALS" = true ]; then
    read -p "Enter your email address: " MAIL_USERNAME
    read -s -p "Enter your password (or app password): " MAIL_PASSWORD
    echo ""
    read -p "Enter sender name (default: Parking App): " SENDER_NAME

    if [ -z "$SENDER_NAME" ]; then
        SENDER_NAME="Parking App"
    fi

    MAIL_DEFAULT_SENDER="$SENDER_NAME <$MAIL_USERNAME>"
else
    MAIL_USERNAME=""
    MAIL_PASSWORD=""
    MAIL_DEFAULT_SENDER="Parking App <noreply@parkingapp.local>"
fi

echo ""
echo "📝 Updating .env file..."

# Remove existing email config lines
sed -i.bak '/^MAIL_/d' .env

# Add new email configuration
cat >> .env << EOF

# Email Configuration
MAIL_SERVER=$MAIL_SERVER
MAIL_PORT=$MAIL_PORT
MAIL_USE_TLS=$([ "$MAIL_PORT" = "1025" ] && echo "false" || echo "true")
MAIL_USERNAME=$MAIL_USERNAME
MAIL_PASSWORD=$MAIL_PASSWORD
MAIL_DEFAULT_SENDER=$MAIL_DEFAULT_SENDER
EOF

echo "✅ Email configuration updated!"
echo ""
echo "🔐 Security Notes:"
if [[ $MAIL_SERVER == *"gmail"* ]]; then
    echo "   • For Gmail, use an App Password instead of your regular password"
    echo "   • Enable 2-factor authentication on your Gmail account"
    echo "   • Generate App Password: https://support.google.com/accounts/answer/185833"
elif [[ $MAIL_SERVER == *"outlook"* ]]; then
    echo "   • For Outlook, you may need to enable 'Less secure app access'"
    echo "   • Or use App Password if 2FA is enabled"
elif [[ $MAIL_SERVER == "localhost" ]]; then
    echo "   • MailHog is running locally - no credentials needed"
    echo "   • View emails at: http://localhost:8025"
    echo "   • Perfect for development and testing!"
fi

echo ""
echo "🧪 Testing email configuration..."

# Test email configuration
python3 -c "
import os
import smtplib
from email.mime.text import MIMEText

# Load environment variables
import sys
sys.path.append('.')
from config import Config

try:
    if not Config.MAIL_SERVER:
        print('❌ MAIL_SERVER not found in configuration')
        sys.exit(1)
    
    print(f'📧 Testing connection to {Config.MAIL_SERVER}:{Config.MAIL_PORT}...')
    
    # Test SMTP connection
    with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
        if Config.MAIL_USE_TLS:
            server.starttls()
        
        if Config.MAIL_USERNAME and os.environ.get('MAIL_PASSWORD'):
            server.login(Config.MAIL_USERNAME, os.environ.get('MAIL_PASSWORD'))
            print('✅ SMTP authentication successful!')
        else:
            print('⚠️ No credentials provided, testing connection only')
            
        print('✅ Email configuration is working!')
        
except Exception as e:
    print(f'❌ Email configuration test failed: {e}')
    print('   Please check your credentials and try again')
"

echo ""
echo "🔄 Restart Celery workers to apply new email configuration:"
echo "   ./stop_celery.sh && ./start_celery.sh"
echo ""
echo "🎉 Email setup complete! Users will now receive notifications when CSV exports are ready."
