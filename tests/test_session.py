import pytest

from app.db.crud import create_user, get_user, update_user
from app.services.session import handle_message


def test_diet_command_sets_awaiting_diet(db_session):
    phone = "whatsapp:+910000000001"

    reply = handle_message(db_session, phone, "DIET")
    user = get_user(db_session, phone)

    assert "Please choose your dietary preference" in reply
    assert user.state == "AWAITING_DIET"


def test_diet_command_is_case_insensitive(db_session):
    phone = "whatsapp:+910000000002"

    reply = handle_message(db_session, phone, "diet")

    assert "Please choose your dietary preference" in reply
    assert get_user(db_session, phone).state == "AWAITING_DIET"


@pytest.mark.parametrize(
    "diet",
    ["vegan", "vegetarian", "keto", "no restrictions"],
)
def test_valid_diet_is_saved(db_session, diet):
    phone = "whatsapp:+910000000003"
    create_user(db_session, phone)
    update_user(db_session, phone, state="AWAITING_DIET")

    reply = handle_message(db_session, phone, diet)
    user = get_user(db_session, phone)

    assert user.diet_type == diet
    assert user.state == "IDLE"
    assert "has been saved" in reply


def test_diet_input_is_case_insensitive(db_session):
    phone = "whatsapp:+910000000004"
    create_user(db_session, phone)
    update_user(db_session, phone, state="AWAITING_DIET")

    reply = handle_message(db_session, phone, "VEGAN")
    user = get_user(db_session, phone)

    assert user.diet_type == "vegan"
    assert user.state == "IDLE"
    assert "has been saved" in reply


def test_invalid_diet_is_rejected(db_session):
    phone = "whatsapp:+910000000005"
    create_user(db_session, phone)
    update_user(db_session, phone, state="AWAITING_DIET")

    reply = handle_message(db_session, phone, "paleo")
    user = get_user(db_session, phone)

    assert "Invalid preference" in reply
    assert user.state == "AWAITING_DIET"
    assert user.diet_type is None


def test_ingredients_generate_recipe(db_session, monkeypatch):
    phone = "whatsapp:+910000000006"
    expected_reply = "Mock recipe"

    def fake_generate_recipe(ingredients, preferences):
        assert ingredients == "tomato and onion"
        assert preferences == "Diet: no preference, Taste: no preference"
        return expected_reply

    monkeypatch.setattr(
        "app.services.session.generate_recipe",
        fake_generate_recipe,
    )

    reply = handle_message(
        db_session,
        phone,
        "  tomato and onion  ",
    )

    assert reply == expected_reply


def test_existing_diet_preferences_are_passed_to_recipe(db_session, monkeypatch):
    phone = "whatsapp:+910000000007"
    create_user(db_session, phone)
    update_user(
        db_session,
        phone,
        diet_type="vegan",
        taste_preference="spicy",
    )

    captured = {}

    def fake_generate_recipe(ingredients, preferences):
        captured["ingredients"] = ingredients
        captured["preferences"] = preferences
        return "Mock recipe"

    monkeypatch.setattr(
        "app.services.session.generate_recipe",
        fake_generate_recipe,
    )

    reply = handle_message(db_session, phone, "tofu")

    assert reply == "Mock recipe"
    assert captured["ingredients"] == "tofu"
    assert captured["preferences"] == "Diet: vegan, Taste: spicy"


def test_unexpected_state_resets_to_idle(db_session):
    phone = "whatsapp:+910000000008"
    create_user(db_session, phone)
    update_user(db_session, phone, state="UNKNOWN_STATE")

    reply = handle_message(db_session, phone, "hello")
    user = get_user(db_session, phone)

    assert reply == ("Sorry, let's start again. Send your ingredients to get a recipe.")
    assert user.state == "IDLE"


def test_full_diet_to_recipe_flow(db_session, monkeypatch):
    phone = "whatsapp:+910000000099"

    reply = handle_message(db_session, phone, "DIET")
    assert "Please choose your dietary preference" in reply

    reply = handle_message(db_session, phone, "vegan")
    assert "has been saved" in reply
    assert get_user(db_session, phone).state == "IDLE"

    def fake_generate_recipe(ingredients, preferences):
        assert ingredients == "tofu and rice"
        assert preferences == "Diet: vegan, Taste: no preference"
        return "Mock vegan recipe"

    monkeypatch.setattr(
        "app.services.session.generate_recipe",
        fake_generate_recipe,
    )

    reply = handle_message(db_session, phone, "tofu and rice")
    assert reply == "Mock vegan recipe"
