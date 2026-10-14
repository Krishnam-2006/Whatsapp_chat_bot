from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.services.twilio import send_message


def test_send_message_success(monkeypatch):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = SimpleNamespace(sid="SM123")

    monkeypatch.setattr(
        "app.services.twilio.Client",
        lambda *args, **kwargs: mock_client,
    )

    result = send_message("whatsapp:+910000000001", "Hello!")

    assert result.sid == "SM123"
    mock_client.messages.create.assert_called_once_with(
        from_=pytest.importorskip("app.core.config").settings.twilio_whatsapp_number,
        to="whatsapp:+910000000001",
        body="Hello!",
    )


def test_send_message_truncates_long_body(monkeypatch):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = SimpleNamespace(sid="SM456")

    monkeypatch.setattr(
        "app.services.twilio.Client",
        lambda *args, **kwargs: mock_client,
    )

    body = "A" * 1600
    send_message("whatsapp:+910000000001", body)

    sent_body = mock_client.messages.create.call_args.kwargs["body"]

    assert sent_body.startswith("A" * 1500)
    assert sent_body.endswith("[Recipe truncated]")
    assert len(sent_body) == 1500 + len("\n\n[Recipe truncated]")


def test_send_message_does_not_truncate_short_body(monkeypatch):
    mock_client = MagicMock()
    mock_client.messages.create.return_value = SimpleNamespace(sid="SM789")

    monkeypatch.setattr(
        "app.services.twilio.Client",
        lambda *args, **kwargs: mock_client,
    )

    body = "A" * 1500
    send_message("whatsapp:+910000000001", body)

    assert mock_client.messages.create.call_args.kwargs["body"] == body


def test_send_message_reraises_twilio_error(monkeypatch):
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = RuntimeError("Twilio unavailable")

    monkeypatch.setattr(
        "app.services.twilio.Client",
        lambda *args, **kwargs: mock_client,
    )

    with pytest.raises(RuntimeError, match="Twilio unavailable"):
        send_message("whatsapp:+910000000001", "Hello!")
