import logging

from twilio.rest import Client

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_message(to: str, body: str):
    if len(body) > 1500:
        body = body[:1500] + "\n\n[Recipe truncated]"

    try:
        client = Client(
            settings.twilio_account_sid,
            settings.twilio_auth_token,
        )

        message = client.messages.create(
            from_=settings.twilio_whatsapp_number,
            to=to,
            body=body,
        )

        logger.info("Twilio message sent successfully: %s", message.sid)
        return message

    except Exception:
        logger.exception("Failed to send Twilio message")
        raise
