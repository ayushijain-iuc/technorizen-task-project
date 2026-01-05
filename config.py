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
    EMAIL_FROM: str = "noreply@yourdomain.com"
    EMAIL_FROM_NAME: str = "SSH Manager"
    
    # SMTP (Alternative)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    
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

