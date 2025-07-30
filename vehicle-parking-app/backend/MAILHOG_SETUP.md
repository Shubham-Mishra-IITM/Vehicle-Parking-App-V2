# 📧 MailHog Setup Guide for Vehicle Parking App V2

## 🎯 What is MailHog?

MailHog is a local email testing tool that:
- ✅ Captures all emails sent by your application
- 🌐 Provides a web interface to view emails
- 🔒 Never actually sends emails (perfect for development)
- 📱 Shows how emails will look to recipients
- 🚀 Works without any real email account setup

## 🚀 Setup Options

### Option 1: Using Docker (Recommended)

1. **Start MailHog with Docker:**
```bash
docker run -d \
  --name mailhog \
  -p 1025:1025 \
  -p 8025:8025 \
  mailhog/mailhog
```

2. **Configure your .env file:**
```bash
# MailHog Configuration
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=false
MAIL_USERNAME=
MAIL_PASSWORD=
MAIL_DEFAULT_SENDER=Parking App <noreply@parkingapp.local>
```

3. **Access MailHog Web Interface:**
   - Open: http://localhost:8025
   - View all captured emails here

### Option 2: Install MailHog Directly

1. **Install MailHog:**
```bash
# macOS with Homebrew
brew install mailhog

# Or download binary from GitHub
# https://github.com/mailhog/MailHog/releases
```

2. **Start MailHog:**
```bash
mailhog
```

3. **Configure .env same as Option 1**

## 🧪 Quick Test Setup

Let me create a quick setup script for you:

### 1. Start MailHog (Docker)
```bash
docker run -d --name mailhog -p 1025:1025 -p 8025:8025 mailhog/mailhog
```

### 2. Create .env with MailHog config
```bash
cp .env.example .env
# Then edit .env to use MailHog settings
```

### 3. Restart Celery workers
```bash
./stop_celery.sh && ./start_celery.sh
```

### 4. Trigger CSV export to test
```bash
# Login and trigger export (your existing test)
# Then check http://localhost:8025 for the email
```

## 🎁 Benefits for Development

- **No Real Email Setup**: No need for Gmail app passwords
- **Visual Testing**: See exactly how emails look
- **Debugging**: Inspect email headers, attachments, HTML
- **No Spam**: Won't accidentally send test emails to real users
- **Fast Setup**: Ready in seconds with Docker

## 🔧 Integration with Your App

MailHog will capture the CSV export notification emails that include:
- 📊 Professional email template
- 📎 CSV file attachment with parking history
- 🎨 HTML formatting with emojis
- 📋 Detailed export information

Perfect for testing the complete email workflow!
