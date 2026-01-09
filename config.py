from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore" 
    )

    DATABASE_URL: str = "postgresql://postgres.wjzfjeyjalofyiytdcqf:MMR7xnKiDtkj9bZs@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres"
    

    SECRET_KEY: str = "your-secret-key-here-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    

    SENDGRID_API_KEY: str = ""
    EMAIL_FROM: str = "aayushi.jain@intelliatech.com"
    EMAIL_FROM_NAME: str = "SSH Manager"
    

    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USE_TLS: bool = True
    EMAIL_HOST_USER: str = "aayushi.jain@intelliatech.com"
    EMAIL_HOST_PASSWORD: str = "kydn xwgc hpet gaqe"
    DEFAULT_FROM_EMAIL: str = "aayushi.jain@intelliatech.com"
    

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "aayushi.jain@intelliatech.com"
    SMTP_PASSWORD: str = "kydn xwgc hpet gaqe"
    SMTP_USE_TLS: bool = True
    
    @property
    def smtp_host(self) -> str:
        return self.EMAIL_HOST or self.SMTP_HOST
    
    @property
    def smtp_port(self) -> int:
        return self.EMAIL_PORT if self.EMAIL_HOST else self.SMTP_PORT
    
    @property
    def smtp_user(self) -> str:
        return self.EMAIL_HOST_USER or self.SMTP_USER
    
    @property
    def smtp_password(self) -> str:
        return self.EMAIL_HOST_PASSWORD or self.SMTP_PASSWORD
    
    @property
    def smtp_use_tls(self) -> bool:
        return self.EMAIL_USE_TLS if self.EMAIL_HOST else self.SMTP_USE_TLS
    
    @property
    def email_from_address(self) -> str:
        return self.DEFAULT_FROM_EMAIL or self.EMAIL_HOST_USER or self.EMAIL_FROM
    
    # Application
    APP_NAME: str = "SSH Manager API"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080"
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5242880  
    ALLOWED_EXTENSIONS: str = "jpg,jpeg,png,gif" 
    
    @property
    def allowed_extensions_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.ALLOWED_EXTENSIONS.split(',') if ext.strip()]
    

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
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

