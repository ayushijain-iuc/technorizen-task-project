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
    
    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:


        if settings.SENDGRID_API_KEY and settings.SENDGRID_API_KEY != "your-sendgrid-api-key-here":
            logger.info("Attempting to send email via SendGrid")
            return EmailService._send_via_sendgrid(to_email, subject, html_content, text_content)
        

        smtp_host = settings.smtp_host
        smtp_user = settings.smtp_user
        smtp_password = settings.smtp_password
        
 
        
        if smtp_host and smtp_user and smtp_password:
            logger.info(f"Attempting to send email via SMTP to {to_email}")
            return EmailService._send_via_smtp(to_email, subject, html_content, text_content)
        
        logger.warning("No email service configured. Email not sent.")
        logger.warning(f"SMTP Config - Host: {smtp_host}, User: {smtp_user}, Password: {'Set' if smtp_password else 'Not Set'}")
        return False
    
    @staticmethod
    def _send_via_sendgrid(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
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
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            from_email = settings.email_from_address
            msg['From'] = f"{settings.EMAIL_FROM_NAME} <{from_email}>"
            msg['To'] = to_email
            
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            smtp_host = settings.smtp_host
            smtp_port = settings.smtp_port
            smtp_user = settings.smtp_user
            smtp_password = settings.smtp_password
            smtp_use_tls = settings.smtp_use_tls
            
            logger.info(f"Connecting to SMTP server: {smtp_host}:{smtp_port}, TLS: {smtp_use_tls}, User: {smtp_user}")
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if smtp_use_tls:
                    logger.info("Starting TLS connection...")
                    server.starttls()
                logger.info(f"Logging in as {smtp_user}...")
                server.login(smtp_user, smtp_password)
                logger.info(f"Sending email to {to_email}...")
                server.send_message(msg)
            
            logger.info(f"Email sent successfully via SMTP to {to_email} from {from_email}")
            return True
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication error: {str(e)}")
            logger.error("Please check your email credentials (username and password)")
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP Connection error: {str(e)}")
            logger.error("Please check SMTP host and port settings")
            return False
        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    @staticmethod
    def send_welcome_email(to_email: str, username: str) -> bool:

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

