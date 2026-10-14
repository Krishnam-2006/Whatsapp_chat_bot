from app.models.processed_message import ProcessedMessage


def valid_payload(message_sid="SM_TEST_001", body="tomato and onion"):
    return {
        "From": "whatsapp:+910000000001",
        "Body": body,
        "MessageSid": message_sid,
    }


def enable_valid_signature(monkeypatch):
    monkeypatch.setattr(
        "app.routes.webhook.validator.validate",
        lambda *args, **kwargs: True,
    )


def test_webhook_rejects_invalid_signature(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.webhook.validator.validate",
        lambda *args, **kwargs: False,
    )

    response = client.post("/webhook", data=valid_payload())

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid Twilio signature"


def test_webhook_rejects_missing_sender(client, monkeypatch):
    enable_valid_signature(monkeypatch)
    payload = valid_payload()
    payload["From"] = ""

    response = client.post("/webhook", data=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Sender and message body are required"


def test_webhook_rejects_empty_message(client, monkeypatch):
    enable_valid_signature(monkeypatch)
    payload = valid_payload(body="   ")

    response = client.post("/webhook", data=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Sender and message body are required"


def test_webhook_rejects_missing_message_sid(client, monkeypatch):
    enable_valid_signature(monkeypatch)
    payload = valid_payload()
    payload.pop("MessageSid")

    response = client.post("/webhook", data=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Message SID is required"


def test_webhook_rejects_message_over_1000_characters(client, monkeypatch):
    enable_valid_signature(monkeypatch)

    response = client.post(
        "/webhook",
        data=valid_payload(body="A" * 1001),
    )

    assert response.status_code == 413
    assert response.json()["detail"] == "Message is too long"


def test_webhook_processes_valid_message(
    client,
    monkeypatch,
    db_session,
):
    enable_valid_signature(monkeypatch)

    monkeypatch.setattr(
        "app.routes.webhook.handle_message",
        lambda db, sender, body: "Mock recipe",
    )

    sent_messages = []
    monkeypatch.setattr(
        "app.routes.webhook.send_message",
        lambda sender, body: sent_messages.append((sender, body)),
    )

    response = client.post(
        "/webhook",
        data=valid_payload(message_sid="SM_WEBHOOK_SUCCESS"),
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert sent_messages == [("whatsapp:+910000000001", "Mock recipe")]

    record = (
        db_session.query(ProcessedMessage)
        .filter(ProcessedMessage.message_sid == "SM_WEBHOOK_SUCCESS")
        .first()
    )

    assert record is not None
    assert record.status == "completed"


def test_webhook_does_not_process_completed_duplicate(
    client,
    monkeypatch,
    db_session,
):
    enable_valid_signature(monkeypatch)

    db_session.add(
        ProcessedMessage(
            message_sid="SM_WEBHOOK_DUPLICATE",
            status="completed",
        )
    )
    db_session.commit()

    def unexpected_call(*args, **kwargs):
        raise AssertionError("Duplicate message should not be processed")

    monkeypatch.setattr(
        "app.routes.webhook.handle_message",
        unexpected_call,
    )
    monkeypatch.setattr(
        "app.routes.webhook.send_message",
        unexpected_call,
    )

    response = client.post(
        "/webhook",
        data=valid_payload(message_sid="SM_WEBHOOK_DUPLICATE"),
    )

    assert response.status_code == 200
    assert response.json() == {"status": "duplicate"}


def test_webhook_skips_message_already_processing(
    client,
    monkeypatch,
    db_session,
):
    enable_valid_signature(monkeypatch)

    db_session.add(
        ProcessedMessage(
            message_sid="SM_WEBHOOK_PROCESSING",
            status="processing",
        )
    )
    db_session.commit()

    response = client.post(
        "/webhook",
        data=valid_payload(message_sid="SM_WEBHOOK_PROCESSING"),
    )

    assert response.status_code == 200
    assert response.json() == {"status": "processing"}


def test_webhook_retries_failed_message(
    client,
    monkeypatch,
    db_session,
):
    enable_valid_signature(monkeypatch)

    db_session.add(
        ProcessedMessage(
            message_sid="SM_WEBHOOK_RETRY",
            status="failed",
        )
    )
    db_session.commit()

    monkeypatch.setattr(
        "app.routes.webhook.handle_message",
        lambda db, sender, body: "Retry recipe",
    )
    monkeypatch.setattr(
        "app.routes.webhook.send_message",
        lambda sender, body: None,
    )

    response = client.post(
        "/webhook",
        data=valid_payload(message_sid="SM_WEBHOOK_RETRY"),
    )

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

    record = (
        db_session.query(ProcessedMessage)
        .filter(ProcessedMessage.message_sid == "SM_WEBHOOK_RETRY")
        .first()
    )

    assert record.status == "completed"


def test_webhook_marks_message_failed_when_sending_fails(
    client,
    monkeypatch,
    db_session,
):
    enable_valid_signature(monkeypatch)

    monkeypatch.setattr(
        "app.routes.webhook.handle_message",
        lambda db, sender, body: "Mock recipe",
    )

    def fail_to_send(sender, body):
        raise RuntimeError("Twilio unavailable")

    monkeypatch.setattr(
        "app.routes.webhook.send_message",
        fail_to_send,
    )

    response = client.post(
        "/webhook",
        data=valid_payload(message_sid="SM_WEBHOOK_FAILURE"),
    )

    assert response.status_code == 500
    assert response.json()["detail"] == "Message processing failed"

    record = (
        db_session.query(ProcessedMessage)
        .filter(ProcessedMessage.message_sid == "SM_WEBHOOK_FAILURE")
        .first()
    )

    assert record is not None
    assert record.status == "failed"
