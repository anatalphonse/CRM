from email.message import EmailMessage
import aiosmtplib
import os

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = 587
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")


async def send_verification_email(to_email: str, token: str):
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = "Verfiy your email"

    verify_url = f"http://localhost:8000/auth/verify-email?token={token}"
    msg.set_content(f"Click to verify: {verify_url}")

    await aiosmtplib.send(msg, hostname=SMTP_HOST, port=SMTP_PORT, username=SMTP_USER, password=SMTP_PASS, start_tls=True)


async def send_reset_email(to_email: str, token: str):
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = "Reset Your Password"

    reset_url = f"http://localhost:8000/api/v1/auth/reset-password?token={token}"
    msg.set_content(f"Click here to reset your password: {reset_url}")

    await aiosmtplib.send(msg, hostname=SMTP_HOST, port=SMTP_PORT, username=SMTP_USER, password=SMTP_PASS, start_tls=True)
