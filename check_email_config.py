#!/usr/bin/env python3
"""
Quick script to check email configuration from .env file
"""
import os
from pathlib import Path

print("=" * 60)
print("Checking .env file for email configuration")
print("=" * 60)

env_file = Path(".env")
if not env_file.exists():
    print("❌ .env file not found!")
    exit(1)

print(f"\n✅ .env file found at: {env_file.absolute()}\n")

# Read .env file
email_vars = {}
with open(env_file, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if 'EMAIL' in key.upper() or 'SMTP' in key.upper():
                email_vars[key] = value

print("Email-related variables found in .env file:")
print("-" * 60)
for key, value in sorted(email_vars.items()):
    if 'PASSWORD' in key.upper():
        display_value = '***' if value else 'Not Set'
    else:
        display_value = value if value else 'Not Set'
    print(f"  {key:25} = {display_value}")

print("\n" + "=" * 60)
print("Checking if required variables are set:")
print("=" * 60)

required_vars = {
    'EMAIL_HOST': 'smtp.gmail.com',
    'EMAIL_PORT': '587',
    'EMAIL_USE_TLS': 'True',
    'EMAIL_HOST_USER': 'your-email@gmail.com',
    'EMAIL_HOST_PASSWORD': 'your-app-password',
    'DEFAULT_FROM_EMAIL': 'your-email@gmail.com'
}

all_set = True
for var, example in required_vars.items():
    value = email_vars.get(var, '')
    if value:
        print(f"✅ {var:25} = {value[:30] if 'PASSWORD' not in var else '***'}")
    else:
        print(f"❌ {var:25} = NOT SET (example: {example})")
        all_set = False

print("\n" + "=" * 60)
if all_set:
    print("✅ All required email variables are set!")
    print("\nNow testing if config can load them...")
    try:
        from config import settings
        print(f"\n✅ Config loaded successfully!")
        print(f"   EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"   EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
        print(f"   EMAIL_HOST_PASSWORD: {'***' if settings.EMAIL_HOST_PASSWORD else 'Not Set'}")
        print(f"   smtp_user (resolved): {settings.smtp_user}")
    except Exception as e:
        print(f"\n❌ Error loading config: {e}")
else:
    print("❌ Some required email variables are missing!")
    print("\nPlease add the missing variables to your .env file.")

