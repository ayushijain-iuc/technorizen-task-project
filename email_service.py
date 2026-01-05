import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Email service using SendGrid or SMTP"""
    
    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send email using SendGrid (preferred) or SMTP fallback
        """
        # Try SendGrid first if API key is configured
        if settings.SENDGRID_API_KEY and settings.SENDGRID_API_KEY != "your-sendgrid-api-key-here":
            return EmailService._send_via_sendgrid(to_email, subject, html_content, text_content)
        
        # Fallback to SMTP
        if settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD:
            return EmailService._send_via_smtp(to_email, subject, html_content, text_content)
        
        logger.warning("No email service configured. Email not sent.")
        return False
    
    @staticmethod
    def _send_via_sendgrid(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send email via SendGrid"""
        try:
            message = Mail(
                from_email=(settings.EMAIL_FROM, settings.EMAIL_FROM_NAME),
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            if text_content:
                message.plain_text_content = text_content
            
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            logger.info(f"Email sent via SendGrid. Status: {response.status_code}")
            return response.status_code in [200, 201, 202]
        except Exception as e:
            logger.error(f"SendGrid error: {str(e)}")
            return False
    
    @staticmethod
    def _send_via_smtp(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send email via SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
            msg['To'] = to_email
            
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_USE_TLS:
                    server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"Email sent via SMTP to {to_email}")
            return True
        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            return False
    
    @staticmethod
    def send_welcome_email(to_email: str, username: str) -> bool:
        """Send welcome email to newly registered user"""
        subject = "Welcome to SSH Manager API"
        html_content = f"""
        <html>
            <body>
                <h2>Welcome {username}!</h2>
                <p>Thank you for registering with SSH Manager API.</p>
                <p>You can now start managing your remote Linux servers securely.</p>
                <p>Best regards,<br>SSH Manager Team</p>
            </body>
        </html>
        """
        text_content = f"Welcome {username}!\n\nThank you for registering with SSH Manager API."
        return EmailService.send_email(to_email, subject, html_content, text_content)
    
    @staticmethod
    def send_command_execution_email(
        to_email: str,
        server_name: str,
        command: str,
        success: bool,
        output: Optional[str] = None,
        error: Optional[str] = None
    ) -> bool:
        """Send email notification about command execution"""
        subject = f"Command Execution {'Success' if success else 'Failed'} - {server_name}"
        status_text = "succeeded" if success else "failed"
        
        html_content = f"""
        <html>
            <body>
                <h2>Command Execution Notification</h2>
                <p><strong>Server:</strong> {server_name}</p>
                <p><strong>Command:</strong> <code>{command}</code></p>
                <p><strong>Status:</strong> {status_text}</p>
                {f'<p><strong>Output:</strong><br><pre>{output[:500]}</pre></p>' if output else ''}
                {f'<p><strong>Error:</strong><br><pre>{error[:500]}</pre></p>' if error else ''}
                <p>Best regards,<br>SSH Manager Team</p>
            </body>
        </html>
        """
        
        text_content = f"Command Execution Notification\n\nServer: {server_name}\nCommand: {command}\nStatus: {status_text}"
        if output:
            text_content += f"\n\nOutput:\n{output[:500]}"
        if error:
            text_content += f"\n\nError:\n{error[:500]}"
        
        return EmailService.send_email(to_email, subject, html_content, text_content)

