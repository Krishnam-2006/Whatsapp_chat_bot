from app.db.crud import create_user, get_user, update_user
from app.services.groq import generate_recipe


def handle_message(db, whatsapp_number, message):
    user = get_user(db, whatsapp_number)

    if not user:
        user = create_user(db, whatsapp_number)

    current_state = user.state
    message = message.strip()

    if current_state == "IDLE":
        if message.upper() == "DIET":
            update_user(db, whatsapp_number, state="AWAITING_DIET")
            reply_text = (
                "Please choose your dietary preference: "
                "vegan, vegetarian, keto, or no restrictions."
            )
        else:
            diet = user.diet_type or "no preference"
            taste = user.taste_preference or "no preference"
            user_preferences = f"Diet: {diet}, Taste: {taste}"
            reply_text = generate_recipe(message, user_preferences)

    elif current_state == "AWAITING_DIET":
        allowed_diets = {
            "vegan",
            "vegetarian",
            "keto",
            "no restrictions",
        }
        diet = message.lower()

        if diet in allowed_diets:
            update_user(
                db,
                whatsapp_number,
                diet_type=diet,
                state="IDLE",
            )
            reply_text = (
                f"Your diet preference ({diet}) has been saved. "
                "What ingredients would you like to use for your next recipe?"
            )
        else:
            reply_text = (
                "Invalid preference. Please choose vegan, vegetarian, "
                "keto, or no restrictions."
            )

    else:
        update_user(db, whatsapp_number, state="IDLE")
        reply_text = "Sorry, let's start again. Send your ingredients to get a recipe."

    return reply_text
