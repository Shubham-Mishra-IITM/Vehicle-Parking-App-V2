# 📧 Email Configuration Guide for Vehicle Parking App V2

## Quick Setup Options

### 🚀 **Option 1: Automated Setup (Recommended)**

Run the setup script to configure email interactively:

```bash
cd /path/to/your/backend
./setup_email.sh
```

### ⚡ **Option 2: Manual Configuration**

Create or edit your `.env` file and add these lines:

#### For Gmail:
```bash
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=Parking App <your-email@gmail.com>
```

#### For Outlook/Hotmail:
```bash
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
MAIL_DEFAULT_SENDER=Parking App <your-email@outlook.com>
```

### 🔐 **Security Setup**

#### Gmail App Password (Recommended):
1. Enable 2-Factor Authentication on your Gmail account
2. Go to: https://support.google.com/accounts/answer/185833
3. Generate an App Password for "Mail"
4. Use the generated 16-character password in MAIL_PASSWORD

#### Outlook Setup:
1. May need to enable "Less secure app access" in security settings
2. Or use App Password if 2FA is enabled

### 🧪 **Test Configuration**

After setup, test your email configuration:

```bash
python3 -c "
from config import Config
print('MAIL_SERVER:', Config.MAIL_SERVER)
print('MAIL_USERNAME:', Config.MAIL_USERNAME)
print('Configuration:', 'Valid' if Config.MAIL_SERVER else 'Invalid')
"
```

### 🔄 **Apply Changes**

Restart Celery workers to apply new email settings:

```bash
./stop_celery.sh
./start_celery.sh
```

### 📋 **What Users Will Receive**

Once configured, users will get emails with:
- ✅ Professional email with parking app branding
- 📊 CSV file attached with complete parking history
- 📁 File details (name, size, generation time)
- 💡 Instructions on how to use the CSV data
- 🔗 Information about the data included

### 🎯 **CSV Export Email Features**

- **Subject**: "🚗 Your Parking History Export is Ready!"
- **Attachment**: Complete parking history CSV
- **Content**: Detailed breakdown of export contents
- **Format**: Professional HTML email with emoji support
- **Data**: All parking sessions with timestamps, costs, locations

### 🐛 **Troubleshooting**

If emails aren't sending:
1. Check Celery worker logs: `tail -f celery_worker.log`
2. Verify SMTP credentials are correct
3. For Gmail, ensure App Password is used (not regular password)
4. Check firewall/network settings for SMTP ports
5. Test SMTP connection manually

### 🌟 **Email Notification Triggers**

Emails are automatically sent when:
- ✅ CSV export job completes successfully
- 📊 File is ready for download
- 🎯 User-triggered async export finishes processing

The system ensures users are promptly notified when their parking data export is ready!
