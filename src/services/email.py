from email.message import EmailMessage

import aiosmtplib

from src.conf.config import config


async def send_verification_email(email: str, token: str) -> None:
    """Send an account email-verification link."""
    url = f"{config.APP_BASE_URL}/api/auth/confirmed_email/{token}"
    message = EmailMessage()
    message["From"] = config.SMTP_FROM
    message["To"] = email
    message["Subject"] = "Confirm your email"
    message.set_content(f"Confirm your email by opening this link: {url}")
    await aiosmtplib.send(
        message,
        hostname=config.SMTP_HOST,
        port=config.SMTP_PORT,
        username=config.SMTP_USER,
        password=config.SMTP_PASSWORD,
        start_tls=True,
    )


async def send_password_reset_email(email: str, token: str) -> None:
    """Send a short-lived password-reset token to an account email address."""
    url = f"{config.APP_BASE_URL}/reset-password?token={token}"
    message = EmailMessage()
    message["From"] = config.SMTP_FROM
    message["To"] = email
    message["Subject"] = "Reset your password"
    message.set_content(f"Reset your password using this link: {url}")
    await aiosmtplib.send(
        message,
        hostname=config.SMTP_HOST,
        port=config.SMTP_PORT,
        username=config.SMTP_USER,
        password=config.SMTP_PASSWORD,
        start_tls=True,
    )
