from fastapi import APIRouter, Request, Depends
from app.db.database import get_db
from app.services.session import handle_message
from app.services.twilio import send_message

router = APIRouter()


@router.post("/webhook")
async def twilio_webhook(request: Request, db=Depends(get_db)):
    form_data = await request.form()

    sender = form_data.get("From")
    message_body = form_data.get("Body")

    reply = handle_message(db, sender, message_body)

    send_message(sender, reply)

    return {"status": "ok"}
