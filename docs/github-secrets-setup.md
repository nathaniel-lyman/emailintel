# GitHub Secrets Setup

This document provides instructions for setting up GitHub repository secrets required for the automated workflows.

## Required Secrets

### OpenAI Configuration
- `OPENAI_API_KEY` - Your OpenAI API key for GPT-4o summarization

### Email Configuration (SMTP)
- `SMTP_HOST` - SMTP server hostname (e.g., smtp.gmail.com)
- `SMTP_PORT` - SMTP port (usually 587 for TLS)
- `SMTP_USERNAME` - SMTP username (email address)
- `SMTP_PASSWORD` - SMTP password (use app password for Gmail)
- `SMTP_FROM_EMAIL` - Email address to send from
- `SMTP_TO_EMAIL` - Email address to send to

### Email Configuration (SendGrid Alternative)
- `SENDGRID_API_KEY` - SendGrid API key
- `SENDGRID_FROM_EMAIL` - Verified sender email address
- `SENDGRID_TO_EMAIL` - Recipient email address

### Flask Configuration
- `FLASK_SECRET_KEY` - Secret key for Flask session management (generate random string)

### Fly.io Deployment
- `FLY_API_TOKEN` - Fly.io API token for deployment

## Setup Instructions

### 1. Access GitHub Repository Secrets
1. Go to your GitHub repository
2. Click on "Settings" tab
3. In the left sidebar, click "Secrets and variables" → "Actions"
4. Click "New repository secret"

### 2. Add Required Secrets

#### OpenAI API Key
- Name: `OPENAI_API_KEY`
- Value: Your OpenAI API key (starts with `sk-`)

#### Email Configuration (Choose SMTP OR SendGrid)

**For SMTP (Gmail example):**
- `SMTP_HOST` = `smtp.gmail.com`
- `SMTP_PORT` = `587`
- `SMTP_USERNAME` = `your-email@gmail.com`
- `SMTP_PASSWORD` = `your-app-password` (not your regular password)
- `SMTP_FROM_EMAIL` = `your-email@gmail.com`
- `SMTP_TO_EMAIL` = `recipient@gmail.com`

**For SendGrid:**
- `SENDGRID_API_KEY` = Your SendGrid API key
- `SENDGRID_FROM_EMAIL` = `your-verified-sender@yourdomain.com`
- `SENDGRID_TO_EMAIL` = `recipient@example.com`

#### Flask Secret Key
- Name: `FLASK_SECRET_KEY`
- Value: Generate a random string (e.g., using `python -c "import secrets; print(secrets.token_hex(32))"`)

#### Fly.io Token (for deployment)
- Name: `FLY_API_TOKEN`
- Value: Your Fly.io API token

### 3. Gmail App Password Setup (if using SMTP)

If using Gmail for SMTP:
1. Enable 2-factor authentication on your Google account
2. Go to Google Account settings → Security → 2-Step Verification
3. At the bottom, click "App passwords"
4. Select "Mail" as the app and "Other" as the device
5. Name it "Retail Price Cut App" and generate
6. Use this 16-character password as `SMTP_PASSWORD`

### 4. Verify Setup

After adding all secrets, you can verify the setup by:
1. Running the daily-digest workflow manually
2. Checking the workflow logs for any authentication errors
3. Confirming emails are received

## Security Best Practices

- Never commit secrets to the repository
- Use app-specific passwords instead of main account passwords
- Regularly rotate API keys and passwords
- Monitor usage and costs for OpenAI API
- Use environment-specific secrets for staging vs production

## Troubleshooting

### Common Issues

1. **OpenAI API errors**: Verify API key is valid and has sufficient credits
2. **Email delivery failures**: Check SMTP credentials and app password setup
3. **Deployment failures**: Ensure Fly.io token has correct permissions
4. **Database errors**: Verify database initialization is working

### Testing Individual Components

```bash
# Test OpenAI API
python -c "from config import Config; print('OpenAI key:', Config.OPENAI_API_KEY[:10] + '...')"

# Test email configuration
python emailer.py test

# Test database setup
python init_db.py check
```

## Support

If you encounter issues:
1. Check GitHub Actions logs for detailed error messages
2. Verify all required secrets are properly set
3. Test individual components locally first
4. Check the application logs in Fly.io dashboard