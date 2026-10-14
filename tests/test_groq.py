from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.groq import generate_recipe


def mock_completion(content):
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


def test_generate_recipe_success(monkeypatch):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completion(
        "Tomato Soup\nPrep time: 10 minutes"
    )

    monkeypatch.setattr(
        "app.services.groq.Groq",
        lambda api_key: mock_client,
    )

    result = generate_recipe("tomato", "Diet: vegan")

    assert result == "Tomato Soup\nPrep time: 10 minutes"
    mock_client.chat.completions.create.assert_called_once()


def test_generate_recipe_strips_whitespace(monkeypatch):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completion(
        "  Tomato Soup  \n"
    )

    monkeypatch.setattr(
        "app.services.groq.Groq",
        lambda api_key: mock_client,
    )

    result = generate_recipe("tomato", "No restrictions")

    assert result == "Tomato Soup"


def test_generate_recipe_empty_content(monkeypatch):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completion("")

    monkeypatch.setattr(
        "app.services.groq.Groq",
        lambda api_key: mock_client,
    )

    result = generate_recipe("tomato", "No restrictions")

    assert result == (
        "Sorry, I'm unable to generate a recipe right now. "
        "Please try again in a few minutes."
    )


def test_generate_recipe_none_content(monkeypatch):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completion(None)

    monkeypatch.setattr(
        "app.services.groq.Groq",
        lambda api_key: mock_client,
    )

    result = generate_recipe("tomato", "No restrictions")

    assert result.startswith("Sorry, I'm unable to generate a recipe")


def test_generate_recipe_api_error(monkeypatch):
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = RuntimeError(
        "Groq API unavailable"
    )

    monkeypatch.setattr(
        "app.services.groq.Groq",
        lambda api_key: mock_client,
    )

    result = generate_recipe("tomato", "No restrictions")

    assert result == (
        "Sorry, I'm unable to generate a recipe right now. "
        "Please try again in a few minutes."
    )


def test_generate_recipe_uses_expected_model_and_options(monkeypatch):
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completion(
        "A simple recipe"
    )

    monkeypatch.setattr(
        "app.services.groq.Groq",
        lambda api_key: mock_client,
    )

    generate_recipe("tomato", "Diet: vegan")

    kwargs = mock_client.chat.completions.create.call_args.kwargs

    assert kwargs["model"] == "openai/gpt-oss-20b"
    assert kwargs["temperature"] == 0.7
    assert kwargs["max_completion_tokens"] == 1024
    assert kwargs["include_reasoning"] is False
