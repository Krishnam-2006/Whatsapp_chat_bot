import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
from twilio.request_validator import RequestValidator

from app.core.config import settings
from app.db.database import get_db
from app.models.processed_message import ProcessedMessage
from app.services.session import handle_message
from app.services.twilio import send_message

logger = logging.getLogger(__name__)

router = APIRouter()
validator = RequestValidator(settings.twilio_auth_token)


def process_message(
    db: Session,
    sender: str,
    message_body: str,
    message_sid: str,
):
    try:
        db.add(
            ProcessedMessage(
                message_sid=message_sid,
                status="processing",
            )
        )
        db.commit()

    except IntegrityError:
        db.rollback()

        existing = (
            db.query(ProcessedMessage)
            .filter(ProcessedMessage.message_sid == message_sid)
            .first()
        )

        if existing and existing.status == "completed":
            return {"status": "duplicate"}

        if existing and existing.status == "processing":
            cutoff = datetime.now(timezone.utc) - timedelta(minutes=5)

            if existing.updated_at and existing.updated_at < cutoff:
                existing.status = "processing"
                existing.updated_at = datetime.now(timezone.utc)
                db.commit()
            else:
                return {"status": "processing"}

        elif existing and existing.status == "failed":
            existing.status = "processing"
            existing.updated_at = datetime.now(timezone.utc)
            db.commit()

        else:
            raise HTTPException(
                status_code=503,
                detail="Unable to check message status",
            )

    try:
        reply = handle_message(db, sender, message_body)
        send_message(sender, reply)

        processed = (
            db.query(ProcessedMessage)
            .filter(ProcessedMessage.message_sid == message_sid)
            .first()
        )

        if processed is None:
            raise RuntimeError("Message tracking record disappeared")

        processed.status = "completed"
        db.commit()

        return {"status": "ok"}

    except Exception:
        db.rollback()
        logger.exception("Failed to process incoming message")

        try:
            processed = (
                db.query(ProcessedMessage)
                .filter(ProcessedMessage.message_sid == message_sid)
                .first()
            )

            if processed:
                processed.status = "failed"
                db.commit()

        except Exception:
            db.rollback()
            logger.exception("Failed to update message status")

        raise HTTPException(
            status_code=500,
            detail="Message processing failed",
        )


@router.post("/webhook")
async def twilio_webhook(
    request: Request,
    db: Session = Depends(get_db),  # noqa: B008
):
    form_data = await request.form()

    signature = request.headers.get("X-Twilio-Signature", "")

    if not validator.validate(
        settings.twilio_webhook_url,
        dict(form_data),
        signature,
    ):
        logger.warning("Invalid Twilio signature received")
        raise HTTPException(
            status_code=403,
            detail="Invalid Twilio signature",
        )

    sender = form_data.get("From")
    message_body = form_data.get("Body")
    message_sid = form_data.get("MessageSid")

    if not isinstance(sender, str) or not sender.strip():
        raise HTTPException(
            status_code=400,
            detail="Sender is required",
        )

    if not isinstance(message_body, str) or not message_body.strip():
        send_message(
            sender,
            "Please send some ingredients so I can suggest a recipe.",
        )
        return {"status": "ignored"}

    if not isinstance(message_sid, str) or not message_sid.strip():
        raise HTTPException(
            status_code=400,
            detail="Message SID is required",
        )

    if len(message_body) > 1000:
        raise HTTPException(
            status_code=413,
            detail="Message is too long",
        )

    return await run_in_threadpool(
        process_message,
        db,
        sender,
        message_body.strip(),
        message_sid,
    )
