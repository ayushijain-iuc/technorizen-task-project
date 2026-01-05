#!/usr/bin/env python3
"""
Test script to verify email configuration and send a test email
"""
import logging
from config import settings
from email_service import EmailService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_email_config():
    """Test email configuration"""
    print("=" * 60)
    print("Email Configuration Test")
    print("=" * 60)
    
    # Check SendGrid
    print(f"\n1. SendGrid API Key: {'Set' if settings.SENDGRID_API_KEY and settings.SENDGRID_API_KEY != 'your-sendgrid-api-key-here' else 'Not Set'}")
    
    # Check SMTP settings
    print(f"\n2. SMTP Configuration:")
    print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"   EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"   EMAIL_USE_TLS: {settings.EMAIL_USE_TLS} (type: {type(settings.EMAIL_USE_TLS).__name__})")
    print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"   EMAIL_HOST_PASSWORD: {'***' if settings.EMAIL_HOST_PASSWORD else 'Not Set'}")
    print(f"   DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    
    print(f"\n3. Direct SMTP Configuration:")
    print(f"   SMTP_HOST: {settings.SMTP_HOST}")
    print(f"   SMTP_PORT: {settings.SMTP_PORT}")
    print(f"   SMTP_USER: {settings.SMTP_USER}")
    print(f"   SMTP_PASSWORD: {'***' if settings.SMTP_PASSWORD else 'Not Set'}")
    print(f"   SMTP_USE_TLS: {settings.SMTP_USE_TLS}")
    
    print(f"\n4. Resolved SMTP Settings (via properties):")
    print(f"   smtp_host: {settings.smtp_host}")
    print(f"   smtp_port: {settings.smtp_port}")
    print(f"   smtp_user: {settings.smtp_user}")
    print(f"   smtp_password: {'***' if settings.smtp_password else 'Not Set'}")
    print(f"   smtp_use_tls: {settings.smtp_use_tls} (type: {type(settings.smtp_use_tls).__name__})")
    print(f"   email_from_address: {settings.email_from_address}")
    
    # Check if email service is configured
    smtp_host = settings.smtp_host
    smtp_user = settings.smtp_user
    smtp_password = settings.smtp_password
    
    if settings.SENDGRID_API_KEY and settings.SENDGRID_API_KEY != "your-sendgrid-api-key-here":
        print(f"\n✅ Email service configured: SendGrid")
        return True
    elif smtp_host and smtp_user and smtp_password:
        print(f"\n✅ Email service configured: SMTP")
        return True
    else:
        print(f"\n❌ Email service NOT configured!")
        print(f"   Please set either SENDGRID_API_KEY or SMTP settings in .env file")
        return False

def test_send_email():
    """Test sending an email"""
    print("\n" + "=" * 60)
    print("Testing Email Sending")
    print("=" * 60)
    
    test_email = input("\nEnter your email address to receive test email: ").strip()
    if not test_email:
        print("No email provided. Skipping email test.")
        return False
    
    print(f"\nSending test email to {test_email}...")
    
    success = EmailService.send_email(
        to_email=test_email,
        subject="Test Email from SSH Manager API",
        html_content="""
        <html>
            <body>
                <h2>Test Email</h2>
                <p>This is a test email from SSH Manager API.</p>
                <p>If you received this email, your SMTP configuration is working correctly!</p>
                <p>Best regards,<br>SSH Manager Team</p>
            </body>
        </html>
        """,
        text_content="Test Email\n\nThis is a test email from SSH Manager API.\n\nIf you received this email, your SMTP configuration is working correctly!"
    )
    
    if success:
        print(f"\n✅ Email sent successfully! Please check your inbox at {test_email}")
        return True
    else:
        print(f"\n❌ Failed to send email. Please check the logs above for error details.")
        return False

if __name__ == "__main__":
    try:
        config_ok = test_email_config()
        
        if config_ok:
            print("\n" + "-" * 60)
            send_test = input("Do you want to send a test email? (y/n): ").strip().lower()
            if send_test == 'y':
                test_send_email()
        else:
            print("\nPlease configure email settings in .env file first.")
    except Exception as e:
        logger.error(f"Error during email test: {str(e)}")
        import traceback
        traceback.print_exc()

