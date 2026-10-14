import pytest

from app.db.crud import create_user, get_user, update_user


def test_create_user(db_session):
    phone = "whatsapp:+910000000101"

    user = create_user(db_session, phone)

    assert user.whatsapp_number == phone
    assert user.state == "IDLE"
    assert user.diet_type is None
    assert user.taste_preference is None


def test_get_existing_user(db_session):
    phone = "whatsapp:+910000000102"
    create_user(db_session, phone)

    user = get_user(db_session, phone)

    assert user is not None
    assert user.whatsapp_number == phone


def test_get_nonexistent_user_returns_none(db_session):
    user = get_user(db_session, "whatsapp:+910000000103")

    assert user is None


def test_create_duplicate_user_returns_existing_user(db_session):
    phone = "whatsapp:+910000000104"

    first_user = create_user(db_session, phone)
    second_user = create_user(db_session, phone)

    assert first_user.whatsapp_number == second_user.whatsapp_number
    assert first_user is second_user


def test_update_user_state(db_session):
    phone = "whatsapp:+910000000105"
    create_user(db_session, phone)

    user = update_user(db_session, phone, state="AWAITING_DIET")

    assert user.state == "AWAITING_DIET"


def test_update_user_diet_and_taste(db_session):
    phone = "whatsapp:+910000000106"
    create_user(db_session, phone)

    user = update_user(
        db_session,
        phone,
        diet_type="vegan",
        taste_preference="spicy",
    )

    assert user.diet_type == "vegan"
    assert user.taste_preference == "spicy"


def test_update_multiple_fields(db_session):
    phone = "whatsapp:+910000000107"
    create_user(db_session, phone)

    user = update_user(
        db_session,
        phone,
        state="AWAITING_DIET",
        diet_type="vegetarian",
        taste_preference="mild",
    )

    assert user.state == "AWAITING_DIET"
    assert user.diet_type == "vegetarian"
    assert user.taste_preference == "mild"


def test_update_nonexistent_user_returns_none(db_session):
    user = update_user(
        db_session,
        "whatsapp:+910000000108",
        state="IDLE",
    )

    assert user is None


def test_update_user_rejects_invalid_field(db_session):
    phone = "whatsapp:+910000000109"
    create_user(db_session, phone)

    with pytest.raises(ValueError, match="Invalid user fields"):
        update_user(db_session, phone, unknown_field="value")


def test_invalid_field_does_not_change_user(db_session):
    phone = "whatsapp:+910000000110"
    create_user(db_session, phone)

    with pytest.raises(ValueError):
        update_user(
            db_session,
            phone,
            state="AWAITING_DIET",
            invalid_field="value",
        )

    user = get_user(db_session, phone)
    assert user.state == "IDLE"
