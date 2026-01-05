from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields in .env file
    )
    # Database
    DATABASE_URL: str = "postgresql://postgres.wjzfjeyjalofyiytdcqf:MMR7xnKiDtkj9bZs@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-here-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email (SendGrid)
    SENDGRID_API_KEY: str = ""
    EMAIL_FROM: str = "aayushi.jain@intelliatech.com"
    EMAIL_FROM_NAME: str = "SSH Manager"
    
    # SMTP Configuration (Hardcoded - can be overridden via .env file)
    # Django-style (will be mapped to SMTP settings)
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USE_TLS: bool = True
    EMAIL_HOST_USER: str = "aayushi.jain@intelliatech.com"
    EMAIL_HOST_PASSWORD: str = "kydn xwgc hpet gaqe"
    DEFAULT_FROM_EMAIL: str = "aayushi.jain@intelliatech.com"
    
    # Direct SMTP settings (alternative to Django-style)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "aayushi.jain@intelliatech.com"
    SMTP_PASSWORD: str = "kydn xwgc hpet gaqe"
    SMTP_USE_TLS: bool = True
    
    @property
    def smtp_host(self) -> str:
        """Get SMTP host from Django EMAIL_HOST or SMTP_HOST"""
        return self.EMAIL_HOST or self.SMTP_HOST
    
    @property
    def smtp_port(self) -> int:
        """Get SMTP port from Django EMAIL_PORT or SMTP_PORT"""
        return self.EMAIL_PORT if self.EMAIL_HOST else self.SMTP_PORT
    
    @property
    def smtp_user(self) -> str:
        """Get SMTP user from Django EMAIL_HOST_USER or SMTP_USER"""
        return self.EMAIL_HOST_USER or self.SMTP_USER
    
    @property
    def smtp_password(self) -> str:
        """Get SMTP password from Django EMAIL_HOST_PASSWORD or SMTP_PASSWORD"""
        return self.EMAIL_HOST_PASSWORD or self.SMTP_PASSWORD
    
    @property
    def smtp_use_tls(self) -> bool:
        """Get SMTP TLS setting from Django EMAIL_USE_TLS or SMTP_USE_TLS"""
        return self.EMAIL_USE_TLS if self.EMAIL_HOST else self.SMTP_USE_TLS
    
    @property
    def email_from_address(self) -> str:
        """Get email from address, prioritizing DEFAULT_FROM_EMAIL, then EMAIL_HOST_USER, then EMAIL_FROM"""
        return self.DEFAULT_FROM_EMAIL or self.EMAIL_HOST_USER or self.EMAIL_FROM
    
    # Application
    APP_NAME: str = "SSH Manager API"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5242880  # 5MB
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,gif"  # Comma-separated string
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get ALLOWED_EXTENSIONS as a list"""
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(',') if ext.strip()]
    
    # Security - Dangerous commands to block
    BLOCKED_COMMANDS: List[str] = [
        "rm -rf /",
        "rm -rf /*",
        ":(){ :|:& };:",
        "mkfs",
        "dd if=/dev/zero",
        "> /dev/sda",
        "chmod -R 777 /",
        "format c:",
        "del /f /s /q",
    ]
    


settings = Settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

