from twilio.rest import Client
from app.core.config import settings


def send_message(to, body):
    client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

    # Twilio WhatsApp message limit protection
    if len(body) > 1500:
        body = body[:1500] + "\n\n[Recipe truncated]"

    print(f"Sending message with length: {len(body)}")

    return client.messages.create(
        from_=settings.twilio_whatsapp_number, to=to, body=body
    )
