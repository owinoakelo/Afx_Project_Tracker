from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_otp_email(recipient_email, otp_code):
    """
    Sends an OTP email to the specified recipient.

    Args:
        recipient_email (str): The recipient's email address.
        otp_code (str): The OTP code to send.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """
    subject = "Your OTP Code"
    message = f"Your OTP code is: {otp_code}. It is valid for {settings.OTP_VALIDITY_MINUTES} minutes."
    from_email = settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(subject, message, from_email, [recipient_email], fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Failed to send OTP email to {recipient_email}: {e}")
        if hasattr(e, 'smtp_code') and hasattr(e, 'smtp_error'):
            logger.error(f"SMTP Code: {e.smtp_code}, SMTP Error: {e.smtp_error}")
        logger.error("Ensure that your email credentials in settings.py are correct.")
        return False
