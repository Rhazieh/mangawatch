import logging

from app.config import settings

logger = logging.getLogger(__name__)


def send_password_reset_email(to_email: str, reset_token: str) -> None:
    reset_url = f"http://localhost:8000/auth/reset-password?token={reset_token}"

    if not settings.sendgrid_api_key:
        # In development, log the link instead of sending — check your server logs
        logger.info("Password reset link for %s: %s", to_email, reset_url)
        return

    # TODO Phase 1+: wire up SendGrid
    # import sendgrid
    # sg = sendgrid.SendGridAPIClient(api_key=settings.sendgrid_api_key)
    # ...
