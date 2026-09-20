from email.message import EmailMessage

import aiosmtplib

from src.conf.config import config


async def send_verification_email(email: str, token: str) -> None:
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
