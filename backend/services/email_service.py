import logging
from typing import Optional

logger = logging.getLogger("accessgov.services.email")


class EmailService:
    """
    SMTP Email Service Placeholder for AccessGov AI.
    Handles dispatching account verification links, password reset tokens, and notifications.
    In development mode, emails are logged to stdout/logger.
    """

    @staticmethod
    def send_verification_email(email: str, token: str) -> bool:
        """
        Sends an email verification link to a newly registered user.
        """
        verification_url = f"http://localhost:8000/api/v1/auth/verify-email?token={token}"
        logger.info(f"[EMAIL SERVICE] Verification email sent to: {email}")
        logger.info(f"[EMAIL SERVICE] Verification URL: {verification_url}")
        print(f"--> [SMTP PLACEHOLDER] Sent Verification Email to {email} | Link: {verification_url}")
        return True

    @staticmethod
    def send_password_reset_email(email: str, token: str) -> bool:
        """
        Sends a password reset link/token to a user requesting reset.
        """
        reset_url = f"http://localhost:8000/api/v1/auth/reset-password?token={token}"
        logger.info(f"[EMAIL SERVICE] Password reset email sent to: {email}")
        logger.info(f"[EMAIL SERVICE] Password Reset URL: {reset_url}")
        print(f"--> [SMTP PLACEHOLDER] Sent Password Reset Email to {email} | Token: {token}")
        return True


email_service = EmailService()
